from django.contrib import admin
from accounts.models import UserProfile


# Desregistrar o admin existente se estiver registrado
try:
    admin.site.unregister(UserProfile)
    print("UserProfile admin desregistrado")
except admin.sites.NotRegistered:
    print("UserProfile admin não estava registrado")


class SimpleUserProfileAdmin(admin.ModelAdmin):
    """
    Admin temporário para debug
    """
    list_display = ('id', 'user', 'cpf')
    
    def changelist_view(self, request, extra_context=None):
        print(f"DEBUG SimpleUserProfileAdmin.changelist_view chamado!")
        print(f"  - User: {request.user.username}")
        print(f"  - UserProfile count: {UserProfile.objects.count()}")
        return super().changelist_view(request, extra_context)


# Registrar o novo admin
admin.site.register(UserProfile, SimpleUserProfileAdmin)
print("SimpleUserProfileAdmin registrado com sucesso")
