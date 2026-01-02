"""Script para visualizar permissões dos grupos"""
from django.contrib.auth.models import Group

print("\n" + "="*60)
print("📋 PERMISSÕES DOS GRUPOS")
print("="*60)

for grupo in Group.objects.all().order_by('name'):
    print(f"\n🔹 {grupo.name} ({grupo.permissions.count()} permissões)")
    print("-" * 60)
    
    perms_auth = grupo.permissions.filter(content_type__app_label='auth')
    if perms_auth.exists():
        print("  👥 Gestão de Usuários:")
        for p in perms_auth.order_by('codename'):
            print(f"     - {p.codename}")
    
    perms_servicos = grupo.permissions.filter(content_type__app_label='servicos')
    if perms_servicos.exists():
        print("  🎫 Módulo de Serviços:")
        for p in perms_servicos.order_by('codename'):
            print(f"     - {p.codename}")

print("\n" + "="*60)
