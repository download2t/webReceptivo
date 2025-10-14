from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import csv
import json
from .models import AuditLog, AuditLogSummary


@staff_member_required
def audit_dashboard(request):
    """Dashboard principal de auditoria"""
    # Estatísticas gerais
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_logs': AuditLog.objects.count(),
        'today_logs': AuditLog.objects.filter(timestamp__date=today).count(),
        'week_logs': AuditLog.objects.filter(timestamp__date__gte=week_ago).count(),
        'month_logs': AuditLog.objects.filter(timestamp__date__gte=month_ago).count(),
        'failed_actions': AuditLog.objects.filter(success=False).count(),
    }
    
    # Ações mais comuns (últimos 30 dias)
    common_actions = (AuditLog.objects
                     .filter(timestamp__date__gte=month_ago)
                     .values('action')
                     .annotate(count=Count('action'))
                     .order_by('-count')[:10])
    
    # Usuários mais ativos (últimos 30 dias)
    active_users = (AuditLog.objects
                   .filter(timestamp__date__gte=month_ago, user__isnull=False)
                   .values('user__username')
                   .annotate(count=Count('user'))
                   .order_by('-count')[:10])
    
    # Atividade por dia (últimos 30 dias)
    daily_activity = (AuditLog.objects
                     .filter(timestamp__date__gte=month_ago)
                     .values('timestamp__date')
                     .annotate(count=Count('id'))
                     .order_by('timestamp__date'))
    
    # Logs recentes
    recent_logs = AuditLog.objects.select_related('user', 'content_type')[:20]
    
    context = {
        'stats': stats,
        'common_actions': common_actions,
        'active_users': active_users,
        'daily_activity': list(daily_activity),
        'recent_logs': recent_logs,
        'title': 'Dashboard de Auditoria',
    }
    
    return render(request, 'audit_system/dashboard.html', context)


@staff_member_required
def audit_logs_list(request):
    """Lista filtrada de logs de auditoria"""
    logs = AuditLog.objects.select_related('user', 'content_type').all()
    
    # Filtros
    action_filter = request.GET.get('action')
    user_filter = request.GET.get('user')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    success_filter = request.GET.get('success')
    search_query = request.GET.get('search')
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__gte=date_from_parsed)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__lte=date_to_parsed)
        except ValueError:
            pass
    
    if success_filter:
        success_bool = success_filter.lower() == 'true'
        logs = logs.filter(success=success_bool)
    
    if search_query:
        logs = logs.filter(
            Q(object_repr__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(ip_address__icontains=search_query) |
            Q(error_message__icontains=search_query)
        )
    
    # Paginação
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Choices para filtros
    action_choices = AuditLog.ACTION_CHOICES
    
    context = {
        'page_obj': page_obj,
        'action_choices': action_choices,
        'current_filters': {
            'action': action_filter,
            'user': user_filter,
            'date_from': date_from,
            'date_to': date_to,
            'success': success_filter,
            'search': search_query,
        },
        'title': 'Logs de Auditoria',
    }
    
    return render(request, 'audit_system/logs_list.html', context)


@staff_member_required
def audit_log_detail(request, log_id):
    """Detalhes de um log específico"""
    log = get_object_or_404(AuditLog, pk=log_id)
    
    context = {
        'log': log,
        'title': f'Log #{log_id}',
    }
    
    return render(request, 'audit_system/log_detail.html', context)


@staff_member_required
def audit_export_csv(request):
    """Exporta logs de auditoria para CSV"""
    # Mesmos filtros da lista
    logs = AuditLog.objects.select_related('user', 'content_type').all()
    
    # Aplicar filtros (mesmo código da audit_logs_list)
    action_filter = request.GET.get('action')
    user_filter = request.GET.get('user')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    success_filter = request.GET.get('success')
    search_query = request.GET.get('search')
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__gte=date_from_parsed)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__lte=date_to_parsed)
        except ValueError:
            pass
    
    if success_filter:
        success_bool = success_filter.lower() == 'true'
        logs = logs.filter(success=success_bool)
    
    if search_query:
        logs = logs.filter(
            Q(object_repr__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(ip_address__icontains=search_query) |
            Q(error_message__icontains=search_query)
        )
    
    # Registrar a exportação
    from .signals import log_data_export
    log_data_export(request.user, 'audit_logs_csv', request)
    
    # Criar CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Data/Hora', 'Ação', 'Usuário', 'Objeto', 'Sucesso',
        'IP', 'Alterações', 'Dados Extras', 'Mensagem de Erro'
    ])
    
    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.get_action_display(),
            log.user.username if log.user else '',
            log.object_repr,
            'Sim' if log.success else 'Não',
            log.ip_address or '',
            log.get_changes_display(),
            json.dumps(log.extra_data) if log.extra_data else '',
            log.error_message or '',
        ])
    
    return response


@staff_member_required
@require_http_methods(["GET"])
def audit_api_stats(request):
    """API para estatísticas do dashboard"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Atividade diária
    daily_stats = (AuditLog.objects
                  .filter(timestamp__date__gte=start_date)
                  .values('timestamp__date')
                  .annotate(
                      total=Count('id'),
                      successful=Count('id', filter=Q(success=True)),
                      failed=Count('id', filter=Q(success=False))
                  )
                  .order_by('timestamp__date'))
    
    # Ações por tipo
    action_stats = (AuditLog.objects
                   .filter(timestamp__date__gte=start_date)
                   .values('action')
                   .annotate(count=Count('id'))
                   .order_by('-count'))
    
    # Usuários mais ativos
    user_stats = (AuditLog.objects
                 .filter(timestamp__date__gte=start_date, user__isnull=False)
                 .values('user__username')
                 .annotate(count=Count('id'))
                 .order_by('-count')[:10])
    
    data = {
        'daily_activity': list(daily_stats),
        'action_distribution': list(action_stats),
        'top_users': list(user_stats),
    }
    
    return JsonResponse(data)


@staff_member_required
def user_audit_history(request, user_id):
    """Histórico de auditoria de um usuário específico"""
    from django.contrib.auth.models import User
    
    user = get_object_or_404(User, pk=user_id)
    
    # Logs do usuário (ações realizadas por ele)
    user_logs = AuditLog.objects.filter(user=user).order_by('-timestamp')
    
    # Logs sobre o usuário (ações realizadas nele)
    about_user_logs = AuditLog.objects.filter(
        content_type__model='user',
        object_id=str(user_id)
    ).order_by('-timestamp')
    
    # Paginação
    paginator = Paginator(user_logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'target_user': user,
        'page_obj': page_obj,
        'about_user_logs': about_user_logs[:20],  # Últimas 20
        'title': f'Histórico de {user.username}',
    }
    
    return render(request, 'audit_system/user_history.html', context)
