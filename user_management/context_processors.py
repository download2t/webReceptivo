"""
Context processors para permissões de usuário.
Disponibiliza informações de permissão em todos os templates.
"""

from .permission_helpers import (
    should_show_admin_menu,
    should_show_user_management_link,
    get_user_level,
    get_user_level_display,
    can_access_user_management,
    can_access_admin_panel
)


def user_permissions(request):
    """
    Context processor que adiciona informações de permissão do usuário atual
    em todos os templates.
    """
    context = {
        'user_can_access_admin_menu': False,
        'user_can_manage_users': False,
        'user_can_manage_groups': False,
        'user_can_access_admin_panel': False,
        'user_level': 'usuario_basico',
        'user_level_display': 'Usuário Básico',
    }
    
    if request.user.is_authenticated:
        context.update({
            'user_can_access_admin_menu': should_show_admin_menu(request.user),
            'user_can_manage_users': should_show_user_management_link(request.user),
            'user_can_manage_groups': should_show_user_management_link(request.user),  # Mesma regra para grupos
            'user_can_access_admin_panel': can_access_admin_panel(request.user),
            'user_level': get_user_level(request.user),
            'user_level_display': get_user_level_display(request.user),
        })
    
    return context
