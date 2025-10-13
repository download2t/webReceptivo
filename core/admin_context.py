"""
Context processor para adicionar dados customizados ao admin Django.
"""

from django.contrib.auth.models import User, Group, Permission


def admin_context(request):
    """
    Adiciona contexto customizado para as páginas do admin Django.
    """
    context = {}
    
    # Só adiciona estatísticas se o usuário estiver autenticado e for staff
    if request.user.is_authenticated and request.user.is_staff:
        try:
            context.update({
                'total_users': User.objects.count(),
                'total_groups': Group.objects.count(), 
                'total_permissions': Permission.objects.count(),
                'active_users': User.objects.filter(is_active=True).count(),
            })
        except Exception:
            # Em caso de erro (ex: banco não disponível), usar valores padrão
            context.update({
                'total_users': 0,
                'total_groups': 0,
                'total_permissions': 0, 
                'active_users': 0,
            })
    
    return context
