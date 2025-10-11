#!/usr/bin/env python
"""
Script para testar configurações de login e sessão
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webreceptivo.settings')
django.setup()

from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User

print("🔧 CONFIGURAÇÕES DE AUTENTICAÇÃO E SESSÃO")
print("=" * 60)

print(f"LOGIN_URL: {settings.LOGIN_URL}")
print(f"LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
print(f"LOGOUT_REDIRECT_URL: {settings.LOGOUT_REDIRECT_URL}")
print()

print("📋 CONFIGURAÇÕES DE SESSÃO:")
print(f"SESSION_COOKIE_AGE: {settings.SESSION_COOKIE_AGE} segundos ({settings.SESSION_COOKIE_AGE/3600:.1f} horas)")
print(f"SESSION_EXPIRE_AT_BROWSER_CLOSE: {settings.SESSION_EXPIRE_AT_BROWSER_CLOSE}")
print(f"SESSION_SAVE_EVERY_REQUEST: {settings.SESSION_SAVE_EVERY_REQUEST}")
print()

print("🔗 URLs DISPONÍVEIS:")
try:
    dashboard_url = reverse('core:dashboard')
    print(f"core:dashboard -> {dashboard_url}")
except:
    print("❌ Erro ao resolver core:dashboard")

try:
    home_url = reverse('core:home')
    print(f"core:home -> {home_url}")
except:
    print("❌ Erro ao resolver core:home")

try:
    login_url = reverse('accounts:login')
    print(f"accounts:login -> {login_url}")
except:
    print("❌ Erro ao resolver accounts:login")

print("\n👤 USUÁRIOS NO SISTEMA:")
users = User.objects.all()
for user in users[:3]:  # Mostrar apenas os primeiros 3
    print(f"  • {user.username} - Ativo: {user.is_active} - Staff: {user.is_staff}")

print(f"\n✅ Total: {users.count()} usuários")

print("\n💡 RECOMENDAÇÕES:")
print("1. Após o login, o usuário deve ser redirecionado para /dashboard/dashboard/")
print("2. A sessão deve durar 4 horas por padrão")
print("3. Se marcar 'Lembrar-me', deve durar 7 dias")
