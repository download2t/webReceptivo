"""
Views para configurações da empresa
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from audit_system.decorators import audit_action
from audit_system.models import AuditLog
import json
import pytz
from .models import CompanySettings, SystemSettings, SMTPSettings
from .forms import CompanySettingsForm, SystemSettingsForm, SMTPSettingsForm


def is_admin_user(user):
    """Verifica se o usuário é administrador"""
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@login_required
@user_passes_test(is_admin_user)
def settings_overview(request):
    """Página principal das configurações"""
    company_settings = CompanySettings.get_settings()
    system_settings = SystemSettings.get_settings()
    smtp_settings = SMTPSettings.get_settings()
    
    context = {
        'company_settings': company_settings,
        'system_settings': system_settings,
        'smtp_settings': smtp_settings,
        'current_datetime': system_settings.get_current_datetime(),
        'title': 'Configurações da Empresa'
    }
    
    return render(request, 'company_settings/overview.html', context)


@login_required
@user_passes_test(is_admin_user)
def company_settings_view(request):
    """Configurações da empresa"""
    settings_obj = CompanySettings.get_settings()
    
    if request.method == 'POST':
        # Capturar estado original para auditoria
        original_data = {}
        for field in CompanySettingsForm.Meta.fields:
            original_data[field] = getattr(settings_obj, field, None)
        
        form = CompanySettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            # Detectar mudanças
            changes_data = {}
            for field in form.changed_data:
                old_value = original_data.get(field)
                new_value = form.cleaned_data.get(field)
                changes_data[field] = {
                    'old': str(old_value) if old_value is not None else None,
                    'new': str(new_value) if new_value is not None else None
                }
            
            settings_obj = form.save(commit=False)
            settings_obj.updated_by = request.user
            settings_obj.save()
            
            # Registrar auditoria
            if changes_data:
                settings_obj.log_changes(user=request.user, request=request, changes_data=changes_data)
            
            messages.success(request, 'Configurações da empresa atualizadas com sucesso!')
            return redirect('company_settings:company')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CompanySettingsForm(instance=settings_obj)
    
    context = {
        'form': form,
        'settings': settings_obj,
        'title': 'Dados da Empresa',
        'active_tab': 'company'
    }
    
    return render(request, 'company_settings/company.html', context)


@login_required
@user_passes_test(is_admin_user)
def system_settings_view(request):
    """Configurações de sistema"""
    settings_obj = SystemSettings.get_settings()
    
    if request.method == 'POST':
        # Capturar estado original para auditoria
        original_data = {}
        for field in SystemSettingsForm.Meta.fields:
            original_data[field] = getattr(settings_obj, field, None)
        
        form = SystemSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            # Detectar mudanças
            changes_data = {}
            for field in form.changed_data:
                old_value = original_data.get(field)
                new_value = form.cleaned_data.get(field)
                changes_data[field] = {
                    'old': str(old_value) if old_value is not None else None,
                    'new': str(new_value) if new_value is not None else None
                }
            
            settings_obj = form.save(commit=False)
            settings_obj.updated_by = request.user
            settings_obj.save()
            
            # Registrar auditoria
            if changes_data:
                settings_obj.log_changes(user=request.user, request=request, changes_data=changes_data)
            
            messages.success(request, 'Configurações de sistema atualizadas com sucesso!')
            return redirect('company_settings:system')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = SystemSettingsForm(instance=settings_obj)
    
    context = {
        'form': form,
        'settings': settings_obj,
        'current_datetime': settings_obj.get_current_datetime(),
        'title': 'Configurações de Sistema',
        'active_tab': 'system'
    }
    
    return render(request, 'company_settings/system.html', context)


@login_required
@user_passes_test(is_admin_user)
def smtp_settings_view(request):
    """Configurações de SMTP"""
    settings_obj = SMTPSettings.get_settings()
    
    if request.method == 'POST':
        # Capturar estado original para auditoria
        original_data = {}
        for field in SMTPSettingsForm.Meta.fields:
            original_data[field] = getattr(settings_obj, field, None)
        
        form = SMTPSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            # Detectar mudanças
            changes_data = {}
            for field in form.changed_data:
                old_value = original_data.get(field)
                new_value = form.cleaned_data.get(field)
                # Não registrar senhas nos logs por segurança
                if 'password' in field.lower():
                    changes_data[field] = {
                        'old': '***HIDDEN***' if old_value else None,
                        'new': '***HIDDEN***' if new_value else None
                    }
                else:
                    changes_data[field] = {
                        'old': str(old_value) if old_value is not None else None,
                        'new': str(new_value) if new_value is not None else None
                    }
            
            settings_obj = form.save(commit=False)
            settings_obj.updated_by = request.user
            settings_obj.save()
            
            # Aplicar configurações ao Django se ativadas
            if settings_obj.is_active:
                success = settings_obj.apply_to_django_settings()
                if success:
                    messages.success(request, 'Configurações de SMTP atualizadas e aplicadas ao sistema com sucesso!')
                else:
                    messages.warning(request, 'Configurações salvas, mas houve um problema ao aplicá-las ao sistema.')
            else:
                messages.success(request, 'Configurações de SMTP salvas com sucesso! Ative-as para usar no sistema.')
            
            # Registrar auditoria
            if changes_data:
                settings_obj.log_changes(user=request.user, request=request, changes_data=changes_data)
            
            return redirect('company_settings:smtp')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = SMTPSettingsForm(instance=settings_obj)
    
    context = {
        'form': form,
        'settings': settings_obj,
        'title': 'Configurações de SMTP',
        'active_tab': 'smtp'
    }
    
    return render(request, 'company_settings/smtp.html', context)


@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def test_smtp_connection(request):
    """Testa a conexão SMTP via AJAX"""
    try:
        settings_obj = SMTPSettings.get_settings()
        
        # Atualizar configurações com dados do formulário
        data = json.loads(request.body)
        settings_obj.smtp_server = data.get('smtp_server', settings_obj.smtp_server)
        settings_obj.smtp_port = int(data.get('smtp_port', settings_obj.smtp_port))
        settings_obj.connection_security = data.get('connection_security', settings_obj.connection_security)
        settings_obj.email = data.get('email', settings_obj.email)
        settings_obj.smtp_password = data.get('smtp_password', settings_obj.smtp_password)
        
        # Obter e-mail de teste
        test_email = data.get('test_email', '').strip()
        if not test_email:
            return JsonResponse({
                'success': False,
                'error': 'E-mail de destino é obrigatório para o teste'
            })
        
        # Testar conexão
        success, message = settings_obj.test_connection(test_email=test_email)
        
        # Registrar teste na auditoria
        settings_obj.log_test_connection(
            user=request.user, 
            request=request, 
            success=success, 
            message=message
        )
        
        return JsonResponse({
            'success': success,
            'message': message,
            'last_test_date': settings_obj.last_test_date.strftime('%d/%m/%Y %H:%M:%S') if settings_obj.last_test_date else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao testar conexão: {str(e)}'
        })


@login_required
@user_passes_test(is_admin_user)
def get_current_datetime(request):
    """Retorna data/hora atual no fuso configurado via AJAX"""
    try:
        system_settings = SystemSettings.get_settings()
        current_datetime = system_settings.get_current_datetime()
        
        # Formatação personalizada baseada nas configurações
        date_format = system_settings.date_format
        time_format = system_settings.time_format
        
        # Converter formato do Django para Python
        python_date_format = date_format.replace('d', '%d').replace('m', '%m').replace('Y', '%Y')
        python_time_format = time_format.replace('H', '%H').replace('i', '%M').replace('g', '%I').replace('A', '%p')
        
        formatted_date = current_datetime.strftime(python_date_format)
        formatted_time = current_datetime.strftime(python_time_format)
        formatted_datetime = f"{formatted_date} {formatted_time}"
        
        return JsonResponse({
            'success': True,
            'datetime': formatted_datetime,
            'date': formatted_date,
            'time': formatted_time,
            'timezone': system_settings.timezone
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao obter data/hora: {str(e)}'
        })


@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def validate_cep(request):
    """Valida CEP via ViaCEP API"""
    try:
        import requests
        
        # Pegar dados do POST JSON
        data_request = json.loads(request.body)
        cep = data_request.get('cep', '').replace('-', '').replace('.', '').replace(' ', '')
        
        if len(cep) != 8 or not cep.isdigit():
            return JsonResponse({
                'success': False, 
                'error': 'CEP deve ter 8 dígitos numéricos'
            })
        
        # Consultar API do ViaCEP
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=10)
        
        if response.status_code != 200:
            return JsonResponse({
                'success': False, 
                'error': 'Serviço de CEP indisponível'
            })
            
        data = response.json()
        
        if 'erro' in data or not data.get('logradouro'):
            return JsonResponse({
                'success': False, 
                'error': 'CEP não encontrado'
            })
        
        return JsonResponse({
            'success': True,
            'logradouro': data.get('logradouro', ''),
            'bairro': data.get('bairro', ''),
            'localidade': data.get('localidade', ''),
            'uf': data.get('uf', ''),
            'complemento': data.get('complemento', ''),
            'ibge': data.get('ibge', ''),
            'gia': data.get('gia', ''),
            'ddd': data.get('ddd', '')
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'error': 'Dados inválidos'
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'success': False, 
            'error': f'Erro de conexão: {str(e)}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Erro interno: {str(e)}'
        })
