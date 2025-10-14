#!/usr/bin/env python
"""
Script de demonstração para popular dados de exemplo
na página de Parâmetros da Empresa
"""

import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webreceptivo.settings')
django.setup()

from company_settings.models import CompanySettings, SystemSettings, SMTPSettings
from django.contrib.auth.models import User


def create_demo_data():
    """Criar dados de demonstração para as configurações"""
    
    print("🚀 Configurando dados de demonstração...")
    
    # 1. Configurações da Empresa
    print("📋 Configurando dados da empresa...")
    company, created = CompanySettings.objects.get_or_create(
        pk=1,
        defaults={
            'company_name': 'WebReceptivo Ltda',
            'cnpj_cpf': '77.766.483/0001-64',
            'state_registration': '123456789',
            'street': 'Av. Paulista',
            'number': '1000',
            'complement': 'Conjunto 101',
            'neighborhood': 'Bela Vista',
            'city': 'São Paulo',
            'state': 'SP',
            'zip_code': '01310-100',
            'phone': '(11) 99999-9999',
            'email': 'contato@webreceptivo.com.br'
        }
    )
    
    if created:
        print("   ✅ Dados da empresa criados")
    else:
        print("   ℹ️ Dados da empresa já existem")
    
    # 2. Configurações do Sistema
    print("⚙️ Configurando sistema...")
    system, created = SystemSettings.objects.get_or_create(
        pk=1,
        defaults={
            'date_format': 'd/m/Y',
            'time_format': 'H:i',
            'timezone': 'America/Sao_Paulo'
        }
    )
    
    if created:
        print("   ✅ Configurações do sistema criadas")
    else:
        print("   ℹ️ Configurações do sistema já existem")
    
    # 3. Configurações SMTP (exemplo)
    print("📧 Configurando SMTP de exemplo...")
    smtp, created = SMTPSettings.objects.get_or_create(
        pk=1,
        defaults={
            'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'connection_security': 'tls',
            'email': 'suportesanma@gmail.com',  # Campo único para todas as funções
            'smtp_password': 'ofdf qopt wduz ahxl',
            'use_authentication': True,
            'timeout': 30,
            'is_active': True  # Ativado para funcionar
        }
    )
    
    if created:
        print("   ✅ Configurações SMTP criadas")
    else:
        print("   ℹ️ Configurações SMTP já existem")
    
    # 4. Criar usuário admin se não existir
    print("👤 Verificando usuário administrador...")
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@webreceptivo.com.br',
            password='admin123'
        )
        print("   ✅ Usuário admin criado (usuário: admin, senha: admin123)")
    else:
        print("   ℹ️ Usuário admin já existe")
    
    print("\n🎉 Dados de demonstração configurados com sucesso!")
    print("\n📋 Informações de acesso:")
    print("   🌐 URL: http://127.0.0.1:8000/configuracoes/")
    print("   👤 Usuário: admin")
    print("   🔐 Senha: admin123")
    print("\n📁 Páginas disponíveis:")
    print("   • Visão Geral: http://127.0.0.1:8000/configuracoes/")
    print("   • Dados da Empresa: http://127.0.0.1:8000/configuracoes/empresa/")
    print("   • Sistema: http://127.0.0.1:8000/configuracoes/sistema/")
    print("   • E-mail SMTP: http://127.0.0.1:8000/configuracoes/smtp/")


def reset_demo_data():
    """Limpar todos os dados de demonstração"""
    print("🗑️ Limpando dados de demonstração...")
    
    CompanySettings.objects.all().delete()
    SystemSettings.objects.all().delete()
    SMTPSettings.objects.all().delete()
    
    print("   ✅ Dados limpos com sucesso!")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciar dados de demonstração')
    parser.add_argument(
        '--reset', 
        action='store_true', 
        help='Limpar todos os dados de demonstração'
    )
    
    args = parser.parse_args()
    
    if args.reset:
        reset_demo_data()
    else:
        create_demo_data()
