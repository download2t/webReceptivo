from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin


# Personalizar o admin de usuários
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_level', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 25
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_queryset(self, request):
        """
        Filtra usuários baseado nas regras de permissão do sistema
        """
        qs = super().get_queryset(request)
        
        # Se for superuser, mostra todos os usuários sem filtro
        if request.user.is_superuser:
            return qs
        
        # Para não-superusers, usar nossas regras de permissão customizadas
        from .permission_helpers import get_manageable_users_queryset
        manageable_users = get_manageable_users_queryset(request.user)
        
        # Retornar apenas usuários que o usuário atual pode gerenciar
        return qs.filter(id__in=manageable_users.values_list('id', flat=True))
    
    def has_add_permission(self, request):
        """Verificar se pode adicionar usuários"""
        from .permission_helpers import get_user_level
        user_level = get_user_level(request.user)
        return user_level in ['admin_principal', 'administrador', 'gerente']
    
    def has_change_permission(self, request, obj=None):
        """Verificar se pode editar usuário específico"""
        if obj is None:
            return self.has_add_permission(request)
        
        from .permission_helpers import can_edit_user
        return can_edit_user(request.user, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Verificar se pode deletar usuário específico"""
        if obj is None:
            return super().has_delete_permission(request)
        
        from .permission_helpers import can_delete_user
        return can_delete_user(request.user, obj)
    
    def get_user_level(self, obj):
        """Exibir nível do usuário"""
        from .permission_helpers import get_user_level_display
        return get_user_level_display(obj)
    get_user_level.short_description = 'Nível'


# Personalizar o admin de grupos
class CustomGroupAdmin(BaseGroupAdmin):
    list_display = ('name', 'get_user_count', 'get_permissions_count', 'is_protected')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    
    def get_queryset(self, request):
        """
        Filtra grupos baseado nas regras de permissão do sistema
        """
        qs = super().get_queryset(request)
        
        # Se for superuser, mostra todos os grupos sem filtro
        if request.user.is_superuser:
            return qs
        
        # Para não-superusers, usar nossas regras de permissão customizadas
        from .permission_helpers import get_manageable_groups_queryset
        manageable_groups = get_manageable_groups_queryset(request.user)
        
        # Retornar apenas grupos que o usuário atual pode gerenciar
        return qs.filter(id__in=manageable_groups.values_list('id', flat=True))
    
    def has_add_permission(self, request):
        """Verificar se pode adicionar grupos"""
        from .permission_helpers import can_create_group
        return can_create_group(request.user)
    
    def has_change_permission(self, request, obj=None):
        """Verificar se pode editar grupo específico"""
        if obj is None:
            return self.has_add_permission(request)
        
        from .permission_helpers import can_edit_group
        return can_edit_group(request.user, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Verificar se pode deletar grupo específico"""
        if obj is None:
            return super().has_delete_permission(request)
        
        from .permission_helpers import can_delete_group
        return can_delete_group(request.user, obj)
    
    def get_user_count(self, obj):
        return obj.user_set.count()
    get_user_count.short_description = 'Usuários'
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()
    get_permissions_count.short_description = 'Permissões'
    
    def is_protected(self, obj):
        from .permission_helpers import is_protected_group
        return "🔒 Sim" if is_protected_group(obj) else "✨ Não"
    is_protected.short_description = 'Protegido'


# Re-registrar os modelos com as personalizações
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)

# Personalizar títulos do admin
admin.site.site_header = 'WebReceptivo - Administração'
admin.site.site_title = 'WebReceptivo Admin'
admin.site.index_title = 'Painel de Administração'
