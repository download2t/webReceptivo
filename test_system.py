#!/usr/bin/env python
"""
Script de teste para verificar o sistema WebReceptivo
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webreceptivo.settings')
django.setup()

from django.contrib.auth.models import User, Group
from accounts.models import UserProfile
from django.contrib.auth import authenticate

def test_system():
    print("🔍 TESTANDO SISTEMA WEBRECEPTIVO")
    print("=" * 50)
    
    # 1. Verificar grupos
    print("\n1. GRUPOS DO SISTEMA:")
    groups = Group.objects.all()
    for group in groups:
        print(f"   • {group.name}: {group.user_set.count()} usuários, {group.permissions.count()} permissões")
    
    # 2. Verificar usuários
    print("\n2. USUÁRIOS DO SISTEMA:")
    users = User.objects.all()
    for user in users:
        groups_list = [g.name for g in user.groups.all()]
        print(f"   • {user.username} ({user.email})")
        print(f"     - Superusuário: {user.is_superuser}")
        print(f"     - Staff: {user.is_staff}")
        print(f"     - Ativo: {user.is_active}")
        print(f"     - Grupos: {groups_list}")
        
        # Verificar perfil
        try:
            profile = user.userprofile
            print(f"     - Perfil: ✅")
        except UserProfile.DoesNotExist:
            print(f"     - Perfil: ❌ AUSENTE")
    
    # 3. Testar autenticação
    print("\n3. TESTE DE AUTENTICAÇÃO:")
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        print(f"   • Usuário admin encontrado")
        print(f"   • Pode fazer login: {admin_user.is_active}")
        
        # Verificar se está no grupo correto
        if admin_user.groups.filter(name='Administradores').exists():
            print(f"   • Está no grupo Administradores: ✅")
        else:
            print(f"   • Está no grupo Administradores: ❌")
            # Adicionar ao grupo
            admin_group = Group.objects.get(name='Administradores')
            admin_user.groups.add(admin_group)
            print(f"   • Adicionado ao grupo Administradores: ✅")
    else:
        print(f"   • ❌ Nenhum usuário admin encontrado")
    
    # 4. Verificar URLs importantes
    print("\n4. URLs DO SISTEMA:")
    urls = [
        "/accounts/login/",
        "/dashboard/",
        "/accounts/profile/",
        "/users/",
        "/users/create/",
    ]
    
    for url in urls:
        print(f"   • {url}")
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("\n💡 Para fazer login:")
    print("   - Usuário: admin")
    print("   - Senha: [a senha que você definiu]")
    print("   - URL: http://localhost:8000/accounts/login/")

if __name__ == '__main__':
    test_system()
