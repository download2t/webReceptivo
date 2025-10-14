from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class AuditLog(models.Model):
    """
    Modelo principal para auditoria de todas as ações do sistema.
    Registra mudanças em modelos, ações de usuários e contexto das operações.
    """
    
    # Tipos de ação
    ACTION_CHOICES = [
        # Ações de usuários
        ('USER_CREATED', 'Usuário Criado'),
        ('USER_UPDATED', 'Usuário Atualizado'),
        ('USER_DELETED', 'Usuário Deletado'),
        ('USER_ACTIVATED', 'Usuário Ativado'),
        ('USER_DEACTIVATED', 'Usuário Desativado'),
        ('USER_PASSWORD_CHANGED', 'Senha Alterada'),
        ('USER_LOGIN', 'Login Realizado'),
        ('USER_LOGOUT', 'Logout Realizado'),
        ('USER_LOGIN_FAILED', 'Login Falhado'),
        
        # Ações de grupos
        ('GROUP_CREATED', 'Grupo Criado'),
        ('GROUP_UPDATED', 'Grupo Atualizado'),
        ('GROUP_DELETED', 'Grupo Deletado'),
        ('GROUP_USER_ADDED', 'Usuário Adicionado ao Grupo'),
        ('GROUP_USER_REMOVED', 'Usuário Removido do Grupo'),
        ('GROUP_PERMISSION_ADDED', 'Permissão Adicionada ao Grupo'),
        ('GROUP_PERMISSION_REMOVED', 'Permissão Removida do Grupo'),
        
        # Ações de permissões
        ('PERMISSION_GRANTED', 'Permissão Concedida'),
        ('PERMISSION_REVOKED', 'Permissão Revogada'),
        ('ROLE_CHANGED', 'Papel/Função Alterada'),
        
        # Ações gerais
        ('SYSTEM_ACCESS', 'Acesso ao Sistema'),
        ('DATA_EXPORT', 'Dados Exportados'),
        ('SETTINGS_CHANGED', 'Configurações Alteradas'),
        
        # Extensível para futuro
        ('CUSTOM_ACTION', 'Ação Customizada'),
    ]
    
    # Identificação da ação
    action = models.CharField('Ação', max_length=50, choices=ACTION_CHOICES)
    
    # Referência genérica ao objeto afetado
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Tipo de Objeto'
    )
    object_id = models.CharField('ID do Objeto', max_length=100, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Representação textual do objeto
    object_repr = models.CharField('Representação do Objeto', max_length=200)
    
    # Dados da mudança (JSON)
    changes = models.JSONField(
        'Alterações',
        default=dict,
        blank=True,
        help_text='Dados das alterações realizadas'
    )
    
    # Contexto da ação
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Usuário',
        related_name='audit_logs'
    )
    
    # Dados temporais
    timestamp = models.DateTimeField('Data/Hora', auto_now_add=True, db_index=True)
    
    # Dados de contexto da requisição
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', null=True, blank=True)
    session_key = models.CharField('Chave da Sessão', max_length=40, null=True, blank=True)
    
    # Resultado da ação
    success = models.BooleanField('Sucesso', default=True)
    error_message = models.TextField('Mensagem de Erro', null=True, blank=True)
    
    # Dados extras específicos da ação
    extra_data = models.JSONField(
        'Dados Extras',
        default=dict,
        blank=True,
        help_text='Dados adicionais específicos da ação'
    )
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        
    def __str__(self):
        user_info = f" por {self.user.username}" if self.user else " (sistema)"
        return f"{self.get_action_display()} - {self.object_repr}{user_info}"
    
    def get_changes_display(self):
        """
        Retorna uma representação amigável das mudanças
        """
        if not self.changes:
            return "Nenhuma alteração registrada"
        
        changes_text = []
        for field, change in self.changes.items():
            if isinstance(change, dict) and 'old' in change and 'new' in change:
                old_val = change['old'] or '(vazio)'
                new_val = change['new'] or '(vazio)'
                changes_text.append(f"{field}: {old_val} → {new_val}")
            else:
                changes_text.append(f"{field}: {change}")
        
        return "; ".join(changes_text)
    
    @classmethod
    def log_action(cls, action, obj=None, user=None, changes=None, extra_data=None, 
                   request=None, success=True, error_message=None):
        """
        Método helper para criar logs de auditoria
        """
        log_data = {
            'action': action,
            'user': user,
            'success': success,
            'error_message': error_message,
            'changes': changes or {},
            'extra_data': extra_data or {},
        }
        
        # Dados do objeto
        if obj:
            log_data['content_object'] = obj
            log_data['object_repr'] = str(obj)
        else:
            log_data['object_repr'] = f"Ação: {action}"
        
        # Dados da requisição
        if request:
            log_data.update({
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'session_key': request.session.session_key,
            })
            
            # Se user não foi passado, pegar da requisição
            if not user and hasattr(request, 'user') and request.user.is_authenticated:
                log_data['user'] = request.user
        
        return cls.objects.create(**log_data)
    
    def is_recent(self, minutes=5):
        """
        Verifica se o log é recente (últimos X minutos)
        """
        now = timezone.now()
        return (now - self.timestamp).total_seconds() < (minutes * 60)


class AuditLogSummary(models.Model):
    """
    Modelo para armazenar resumos de auditoria (relatórios pré-calculados)
    """
    date = models.DateField('Data', db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField('Ação', max_length=50)
    count = models.IntegerField('Contador', default=0)
    
    class Meta:
        verbose_name = 'Resumo de Auditoria'
        verbose_name_plural = 'Resumos de Auditoria'
        unique_together = ['date', 'user', 'action']


def get_client_ip(request):
    """
    Extrai o IP real do cliente da requisição
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
