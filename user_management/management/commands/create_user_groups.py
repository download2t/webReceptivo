from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps


class Command(BaseCommand):
    help = 'Criar grupos de usuário padrão com permissões'

    def handle(self, *args, **options):
        self.stdout.write('Criando grupos de usuário padrão...')

        # Grupos e suas permissões
        groups_config = {
            'Administradores': {
                'description': 'Acesso total ao sistema',
                'permissions': [
                    # Usuários
                    'auth.view_user', 'auth.add_user', 'auth.change_user', 'auth.delete_user',
                    'auth.view_group', 'auth.add_group', 'auth.change_group', 'auth.delete_group',
                    'auth.view_permission',
                    
                    # Accounts
                    'accounts.view_userprofile', 'accounts.change_userprofile',
                    
                    # Core (se tiver)
                    # 'core.view_dashboard', 'core.manage_system',
                ]
            },
            
            'Gerentes': {
                'description': 'Gerenciamento de usuários e relatórios',
                'permissions': [
                    # Usuários (sem deletar)
                    'auth.view_user', 'auth.add_user', 'auth.change_user',
                    'auth.view_group',
                    
                    # Accounts
                    'accounts.view_userprofile', 'accounts.change_userprofile',
                ]
            },
            
            'Operadores': {
                'description': 'Operação básica do sistema',
                'permissions': [
                    # Apenas visualização de usuários
                    'auth.view_user',
                    
                    # Accounts básico
                    'accounts.view_userprofile',
                ]
            },
            
            'Usuários Básicos': {
                'description': 'Acesso limitado ao sistema',
                'permissions': [
                    # Apenas próprio perfil
                    'accounts.view_userprofile',
                ]
            }
        }

        # Criar grupos
        for group_name, config in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(f'✓ Grupo "{group_name}" criado')
            else:
                self.stdout.write(f'• Grupo "{group_name}" já existe')
            
            # Adicionar permissões
            permissions_added = 0
            for perm_code in config['permissions']:
                try:
                    app_label, codename = perm_code.split('.')
                    permission = Permission.objects.get(
                        codename=codename,
                        content_type__app_label=app_label
                    )
                    
                    if not group.permissions.filter(id=permission.id).exists():
                        group.permissions.add(permission)
                        permissions_added += 1
                        
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Permissão "{perm_code}" não encontrada')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Erro ao processar "{perm_code}": {e}')
                    )
            
            if permissions_added > 0:
                self.stdout.write(f'  → {permissions_added} permissões adicionadas')

        self.stdout.write(self.style.SUCCESS('\n✅ Grupos criados com sucesso!'))
        
        # Mostrar resumo
        self.stdout.write('\n📋 Resumo dos grupos:')
        for group in Group.objects.all().order_by('name'):
            perm_count = group.permissions.count()
            self.stdout.write(f'  • {group.name}: {perm_count} permissões')
        
        self.stdout.write('\n💡 Para atribuir usuários aos grupos:')
        self.stdout.write('   python manage.py shell')
        self.stdout.write('   >>> from django.contrib.auth.models import User, Group')
        self.stdout.write('   >>> user = User.objects.get(username="seu_usuario")')
        self.stdout.write('   >>> group = Group.objects.get(name="Administradores")')
        self.stdout.write('   >>> user.groups.add(group)')
        
        self.stdout.write('\n🌐 Ou use a interface web: /users/')
