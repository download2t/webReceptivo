"""
Decoradores para facilitar o uso do sistema de auditoria
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from .signals import log_custom_action


def audit_action(action_name, success_message=None, error_message=None):
    """
    Decorador para registrar automaticamente ações customizadas
    
    Usage:
    @audit_action('user_export', 'Dados exportados com sucesso')
    def export_users(request):
        # função implementation
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                result = view_func(request, *args, **kwargs)
                
                # Log de sucesso
                log_custom_action(
                    action_name=action_name,
                    user=getattr(request, 'user', None),
                    request=request,
                    success=True,
                    extra_data={
                        'view_name': view_func.__name__,
                        'args': str(args),
                        'kwargs': {k: str(v) for k, v in kwargs.items()},
                    }
                )
                
                return result
                
            except Exception as e:
                # Log de erro
                log_custom_action(
                    action_name=action_name,
                    user=getattr(request, 'user', None),
                    request=request,
                    success=False,
                    error_message=str(e),
                    extra_data={
                        'view_name': view_func.__name__,
                        'args': str(args),
                        'kwargs': {k: str(v) for k, v in kwargs.items()},
                        'error_type': type(e).__name__,
                    }
                )
                
                # Re-raise a exceção
                raise
                
        return _wrapped_view
    return decorator


def audit_model_action(action_name, model_param='pk'):
    """
    Decorador para registrar ações em modelos específicos
    
    Usage:
    @audit_model_action('user_view', 'user_id')
    def user_detail(request, user_id):
        user = get_object_or_404(User, pk=user_id)
        # função implementation
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Tentar obter o objeto do modelo
            obj = None
            if model_param in kwargs:
                obj_id = kwargs[model_param]
                # Aqui você poderia implementar lógica para detectar automaticamente o modelo
                # Por simplicidade, vamos deixar como None e usar extra_data
            
            try:
                result = view_func(request, *args, **kwargs)
                
                log_custom_action(
                    action_name=action_name,
                    obj=obj,
                    user=getattr(request, 'user', None),
                    request=request,
                    success=True,
                    extra_data={
                        'view_name': view_func.__name__,
                        'object_id': kwargs.get(model_param),
                    }
                )
                
                return result
                
            except Exception as e:
                log_custom_action(
                    action_name=action_name,
                    obj=obj,
                    user=getattr(request, 'user', None),
                    request=request,
                    success=False,
                    error_message=str(e),
                    extra_data={
                        'view_name': view_func.__name__,
                        'object_id': kwargs.get(model_param),
                        'error_type': type(e).__name__,
                    }
                )
                
                raise
                
        return _wrapped_view
    return decorator


def audit_login_required(action_name=None):
    """
    Combinação de login_required com audit_action
    """
    def decorator(view_func):
        if action_name:
            audited_view = audit_action(action_name)(view_func)
        else:
            audited_view = view_func
            
        return login_required(audited_view)
    return decorator
