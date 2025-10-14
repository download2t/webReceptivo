from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json
from .models import AuditLog, AuditLogSummary


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Interface admin para logs de auditoria"""
    
    list_display = [
        'timestamp', 'action_display', 'user_link', 'object_display', 
        'success_icon', 'ip_address'
    ]
    list_filter = [
        'action', 'success', 'timestamp', 'content_type'
    ]
    search_fields = [
        'user__username', 'user__email', 'object_repr', 
        'ip_address', 'error_message'
    ]
    readonly_fields = [
        'timestamp', 'action', 'content_type', 'object_id', 
        'object_repr', 'user', 'ip_address', 'user_agent', 
        'session_key', 'success', 'error_message', 'changes_formatted',
        'extra_data_formatted'
    ]
    
    # Campos agrupados
    fieldsets = (
        ('Informações da Ação', {
            'fields': ('timestamp', 'action', 'success', 'error_message')
        }),
        ('Objeto Afetado', {
            'fields': ('content_type', 'object_id', 'object_repr'),
            'classes': ('collapse',)
        }),
        ('Usuário e Contexto', {
            'fields': ('user', 'ip_address', 'session_key'),
            'classes': ('collapse',)
        }),
        ('Dados Técnicos', {
            'fields': ('user_agent', 'changes_formatted', 'extra_data_formatted'),
            'classes': ('collapse',)
        }),
    )
    
    # Ordenação e paginação
    ordering = ['-timestamp']
    list_per_page = 50
    
    # Remover ações de edição/exclusão
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Campos customizados
    def action_display(self, obj):
        """Exibe a ação com ícone colorido"""
        colors = {
            'USER_CREATED': '#28a745',
            'USER_UPDATED': '#007bff',
            'USER_DELETED': '#dc3545',
            'USER_ACTIVATED': '#28a745',
            'USER_DEACTIVATED': '#ffc107',
            'USER_LOGIN': '#17a2b8',
            'USER_LOGOUT': '#6c757d',
            'USER_LOGIN_FAILED': '#dc3545',
            'GROUP_CREATED': '#28a745',
            'GROUP_UPDATED': '#007bff',
            'GROUP_DELETED': '#dc3545',
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_display.short_description = 'Ação'
    action_display.admin_order_field = 'action'
    
    def user_link(self, obj):
        """Exibe link para o usuário"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'Usuário'
    user_link.admin_order_field = 'user__username'
    
    def object_display(self, obj):
        """Exibe o objeto com link se possível"""
        if obj.content_object and hasattr(obj.content_object, 'get_absolute_url'):
            try:
                url = obj.content_object.get_absolute_url()
                return format_html('<a href="{}" target="_blank">{}</a>', url, obj.object_repr)
            except:
                pass
        return obj.object_repr
    object_display.short_description = 'Objeto'
    
    def success_icon(self, obj):
        """Exibe ícone de sucesso/erro"""
        if obj.success:
            return format_html('<span style="color: #28a745;">✓</span>')
        else:
            return format_html('<span style="color: #dc3545;" title="{}">✗</span>', obj.error_message or 'Erro')
    success_icon.short_description = 'Status'
    success_icon.admin_order_field = 'success'
    
    def changes_formatted(self, obj):
        """Exibe as mudanças formatadas"""
        if not obj.changes:
            return 'Nenhuma alteração'
        
        html = '<ul style="margin: 0; padding-left: 20px;">'
        for field, change in obj.changes.items():
            if isinstance(change, dict) and 'old' in change and 'new' in change:
                old_val = change['old'] or '(vazio)'
                new_val = change['new'] or '(vazio)'
                html += f'<li><strong>{field}:</strong> {old_val} → {new_val}</li>'
            else:
                html += f'<li><strong>{field}:</strong> {change}</li>'
        html += '</ul>'
        return mark_safe(html)
    changes_formatted.short_description = 'Alterações'
    
    def extra_data_formatted(self, obj):
        """Exibe dados extras formatados"""
        if not obj.extra_data:
            return 'Nenhum dado extra'
        
        try:
            formatted = json.dumps(obj.extra_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="font-size: 12px;">{}</pre>', formatted)
        except:
            return str(obj.extra_data)
    extra_data_formatted.short_description = 'Dados Extras'


@admin.register(AuditLogSummary)
class AuditLogSummaryAdmin(admin.ModelAdmin):
    """Interface admin para resumos de auditoria"""
    
    list_display = ['date', 'user', 'action', 'count']
    list_filter = ['date', 'action']
    search_fields = ['user__username', 'action']
    readonly_fields = ['date', 'user', 'action', 'count']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
