"""
Comando para criar usuários de teste para validar o sistema de permissões.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction


class Command(BaseCommand):
    help = 'Cria usuários de teste para validar sistema de permissões'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove usuários de teste existentes antes de criar novos',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Removendo usuários de teste existentes...')
            User.objects.filter(username__in=[
                'admin_teste', 'gerente_teste', 'operador_teste', 'usuario_teste'
            ]).delete()
        
        # Garantir que os grupos existem
        try:
            with transaction.atomic():
                # Criar usuários de teste
                users_created = []
                
                # 1. Admin Teste (Administrador)
                if not User.objects.filter(username='admin_teste').exists():
                    admin_user = User.objects.create_user(
                        username='admin_teste',
                        email='admin@teste.com',
                        password='senha123',
                        first_name='Admin',
                        last_name='Teste',
                        is_staff=True
                    )
                    admin_group = Group.objects.get(name='Administradores')
                    admin_user.groups.add(admin_group)
                    users_created.append('admin_teste (Administrador)')
                
                # 2. Gerente Teste
                if not User.objects.filter(username='gerente_teste').exists():
                    gerente_user = User.objects.create_user(
                        username='gerente_teste',
                        email='gerente@teste.com',
                        password='senha123',
                        first_name='Gerente',
                        last_name='Teste'
                    )
                    gerente_group = Group.objects.get(name='Gerentes')
                    gerente_user.groups.add(gerente_group)
                    users_created.append('gerente_teste (Gerente)')
                
                # 3. Operador Teste
                if not User.objects.filter(username='operador_teste').exists():
                    operador_user = User.objects.create_user(
                        username='operador_teste',
                        email='operador@teste.com',
                        password='senha123',
                        first_name='Operador',
                        last_name='Teste'
                    )
                    operador_group = Group.objects.get(name='Operadores')
                    operador_user.groups.add(operador_group)
                    users_created.append('operador_teste (Operador)')
                
                # 4. Usuário Básico Teste
                if not User.objects.filter(username='usuario_teste').exists():
                    usuario_user = User.objects.create_user(
                        username='usuario_teste',
                        email='usuario@teste.com',
                        password='senha123',
                        first_name='Usuário',
                        last_name='Teste'
                    )
                    usuario_group = Group.objects.get(name='Usuários Básicos')
                    usuario_user.groups.add(usuario_group)
                    users_created.append('usuario_teste (Usuário Básico)')
                
                # Mostrar resultados
                if users_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'\n✅ Usuários criados com sucesso:')
                    )
                    for user in users_created:
                        self.stdout.write(f'  • {user}')
                    
                    self.stdout.write(
                        self.style.WARNING('\n🔑 Todos os usuários têm senha: senha123')
                    )
                    
                    self.stdout.write('\n📋 Para testar permissões:')
                    self.stdout.write('  1. Faça login com cada usuário')
                    self.stdout.write('  2. Verifique quais menus aparecem')
                    self.stdout.write('  3. Teste as operações de usuários e grupos')
                    
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Todos os usuários de teste já existem')
                    )
                    self.stdout.write('Use --reset para recriar os usuários')
        
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Erro: Execute primeiro "python manage.py setup_groups" '
                    'para criar os grupos básicos'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar usuários: {e}')
            )
