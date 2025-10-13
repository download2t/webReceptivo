from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'cpf', 'telefone', 'cidade', 'estado')
    list_filter = ('estado', 'tema_preferido', 'user__is_active')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'cpf', 'telefone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Informações Pessoais', {
            'fields': ('cpf', 'data_nascimento', 'avatar')
        }),
        ('Contato', {
            'fields': ('telefone', 'celular')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep'),
            'classes': ('collapse',)
        }),
        ('Preferências', {
            'fields': ('tema_preferido',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Filtra perfis baseado nas regras de permissão do sistema
        """
        qs = super().get_queryset(request)
        
        # Se for superuser, mostra todos os perfis sem filtro
        if request.user.is_superuser:
            return qs
        
        # Para não-superusers, filtrar baseado nos usuários que pode gerenciar
        from user_management.permission_helpers import get_manageable_users_queryset
        manageable_users = get_manageable_users_queryset(request.user)
        
        # Retornar apenas perfis dos usuários que o usuário atual pode gerenciar
        return qs.filter(user__id__in=manageable_users.values_list('id', flat=True))
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Nome Completo'
 