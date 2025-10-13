#!/usr/bin/env python
"""
Script de debug para verificar perfis de usuário no admin
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebReceptivo.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from accounts.models import UserProfile
from django.contrib.auth.models import User
from django.contrib import admin

def debug_userprofile_admin():
    print("=== DEBUG USERPROFILE ADMIN ===")
    
    # 1. Verificar modelos
    print(f"1. Total usuários: {User.objects.count()}")
    print(f"1. Total perfis: {UserProfile.objects.count()}")
    
    # 2. Verificar registro no admin
    print(f"\n2. UserProfile registrado no admin: {UserProfile in admin.site._registry}")
    
    if UserProfile in admin.site._registry:
        admin_class = admin.site._registry[UserProfile]
        print(f"2. Classe admin: {admin_class}")
    
    # 3. Verificar perfis individualmente
    print(f"\n3. Listagem detalhada dos perfis:")
    for profile in UserProfile.objects.all():
        print(f"   - ID: {profile.id}")
        print(f"     User: {profile.user.username} (ID: {profile.user.id})")
        print(f"     Nome: {profile.user.get_full_name()}")
        print(f"     CPF: {profile.cpf}")
        print(f"     Created: {profile.created_at}")
        print()
    
    # 4. Verificar relacionamento reverso
    print(f"4. Teste de relacionamento reverso:")
    for user in User.objects.all():
        try:
            profile = user.profile
            print(f"   ✓ {user.username} -> Profile ID {profile.id}")
        except UserProfile.DoesNotExist:
            print(f"   ✗ {user.username} -> SEM PROFILE")
    
    # 5. Verificar queryset do admin
    from accounts.admin import UserProfileAdmin
    from django.http import HttpRequest
    
    print(f"\n5. Teste do admin queryset:")
    request = HttpRequest()
    request.user = User.objects.filter(is_superuser=True).first()
    
    admin_instance = UserProfileAdmin(UserProfile, admin.site)
    queryset = admin_instance.get_queryset(request)
    print(f"   Queryset count: {queryset.count()}")
    
    for profile in queryset:
        print(f"   - {profile.user.username}: {profile}")

if __name__ == '__main__':
    debug_userprofile_admin()
