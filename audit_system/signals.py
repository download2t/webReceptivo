"""
Signals para capturar automaticamente ações do sistema e registrar logs de auditoria.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.utils import timezone
from .models import AuditLog
import threading

# Thread local storage para armazenar dados da requisição
_local = threading.local()


def set_current_request(request):
    """Define a requisição atual no thread local"""
    _local.request = request


def get_current_request():
    """Recupera a requisição atual do thread local"""
    return getattr(_local, 'request', None)


def get_field_changes(instance, old_instance=None):
    """
    Compara dois instances do mesmo modelo e retorna as mudanças
    """
    if not old_instance:
        return {}
    
    changes = {}
    for field in instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(instance, field_name, None)
        
        # Ignorar campos de timestamp automáticos
        if field_name in ['created_at', 'updated_at', 'last_login', 'date_joined']:
            continue
            
        if old_value != new_value:
            changes[field_name] = {
                'old': str(old_value) if old_value is not None else None,
                'new': str(new_value) if new_value is not None else None
            }
    
    return changes


# Store original instances for comparison
original_instances = {}


@receiver(pre_save, sender=User)
def store_original_user(sender, instance, **kwargs):
    """Armazena o estado original do usuário antes da alteração"""
    if instance.pk:
        try:
            original_instances[f"user_{instance.pk}"] = User.objects.get(pk=instance.pk)
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Registra mudanças em usuários"""
    request = get_current_request()
    
    if created:
        action = 'USER_CREATED'
        changes = {}
    else:
        action = 'USER_UPDATED'
        original = original_instances.pop(f"user_{instance.pk}", None)
        changes = get_field_changes(instance, original)
        
        # Se não houve mudanças significativas, não registrar
        if not changes:
            return
    
    AuditLog.log_action(
        action=action,
        obj=instance,
        request=request,
        changes=changes
    )


@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """Registra exclusão de usuários"""
    request = get_current_request()
    
    AuditLog.log_action(
        action='USER_DELETED',
        obj=None,  # Objeto já foi deletado
        request=request,
        extra_data={
            'deleted_user_id': instance.pk,
            'deleted_user_username': instance.username,
            'deleted_user_email': instance.email,
        }
    )


@receiver(pre_save, sender=Group)
def store_original_group(sender, instance, **kwargs):
    """Armazena o estado original do grupo antes da alteração"""
    if instance.pk:
        try:
            original_instances[f"group_{instance.pk}"] = Group.objects.get(pk=instance.pk)
        except Group.DoesNotExist:
            pass


@receiver(post_save, sender=Group)
def log_group_changes(sender, instance, created, **kwargs):
    """Registra mudanças em grupos"""
    request = get_current_request()
    
    if created:
        action = 'GROUP_CREATED'
        changes = {}
    else:
        action = 'GROUP_UPDATED'
        original = original_instances.pop(f"group_{instance.pk}", None)
        changes = get_field_changes(instance, original)
        
        if not changes:
            return
    
    AuditLog.log_action(
        action=action,
        obj=instance,
        request=request,
        changes=changes
    )


@receiver(post_delete, sender=Group)
def log_group_deletion(sender, instance, **kwargs):
    """Registra exclusão de grupos"""
    request = get_current_request()
    
    AuditLog.log_action(
        action='GROUP_DELETED',
        obj=None,
        request=request,
        extra_data={
            'deleted_group_id': instance.pk,
            'deleted_group_name': instance.name,
        }
    )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Registra login de usuário"""
    AuditLog.log_action(
        action='USER_LOGIN',
        obj=user,
        request=request,
        extra_data={
            'login_timestamp': timezone.now().isoformat()
        }
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Registra logout de usuário"""
    AuditLog.log_action(
        action='USER_LOGOUT',
        obj=user,
        request=request,
        extra_data={
            'logout_timestamp': timezone.now().isoformat()
        }
    )


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Registra tentativas de login falhadas"""
    username = credentials.get('username', 'unknown')
    
    AuditLog.log_action(
        action='USER_LOGIN_FAILED',
        obj=None,
        request=request,
        success=False,
        extra_data={
            'attempted_username': username,
            'failure_timestamp': timezone.now().isoformat()
        }
    )


# Funções helper para registrar ações específicas
def log_password_change(user, request=None):
    """Registra mudança de senha"""
    AuditLog.log_action(
        action='USER_PASSWORD_CHANGED',
        obj=user,
        request=request
    )


def log_user_activation(user, activated, request=None):
    """Registra ativação/desativação de usuário"""
    action = 'USER_ACTIVATED' if activated else 'USER_DEACTIVATED'
    AuditLog.log_action(
        action=action,
        obj=user,
        request=request,
        changes={'is_active': {'old': not activated, 'new': activated}}
    )


def log_group_membership_change(user, group, added, request=None):
    """Registra adição/remoção de usuário em grupo"""
    action = 'GROUP_USER_ADDED' if added else 'GROUP_USER_REMOVED'
    AuditLog.log_action(
        action=action,
        obj=group,
        request=request,
        extra_data={
            'user_id': user.pk,
            'user_username': user.username,
            'membership_action': 'added' if added else 'removed'
        }
    )


def log_permission_change(obj, permission, granted, request=None):
    """Registra concessão/revogação de permissão"""
    action = 'PERMISSION_GRANTED' if granted else 'PERMISSION_REVOKED'
    AuditLog.log_action(
        action=action,
        obj=obj,
        request=request,
        extra_data={
            'permission': str(permission),
            'permission_action': 'granted' if granted else 'revoked'
        }
    )


def log_data_export(user, data_type, request=None):
    """Registra exportação de dados"""
    AuditLog.log_action(
        action='DATA_EXPORT',
        obj=None,
        request=request,
        extra_data={
            'data_type': data_type,
            'export_timestamp': timezone.now().isoformat()
        }
    )


def log_settings_change(setting_name, old_value, new_value, request=None):
    """Registra mudança de configuração"""
    AuditLog.log_action(
        action='SETTINGS_CHANGED',
        obj=None,
        request=request,
        changes={
            setting_name: {
                'old': str(old_value),
                'new': str(new_value)
            }
        }
    )


def log_custom_action(action_name, obj=None, user=None, changes=None, 
                     extra_data=None, request=None, success=True, error_message=None):
    """Registra ação customizada"""
    AuditLog.log_action(
        action='CUSTOM_ACTION',
        obj=obj,
        user=user,
        request=request,
        changes=changes,
        extra_data={
            'custom_action_name': action_name,
            **(extra_data or {})
        },
        success=success,
        error_message=error_message
    )
