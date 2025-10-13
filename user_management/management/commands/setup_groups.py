"""
Command para criar os grupos básicos do sistema de permissões.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Cria os grupos básicos do sistema de permissões'
    
    def handle(self, *args, **options):
        # Definir grupos e suas permissões
        groups_permissions = {
            'Administradores': [
                'auth.add_user',
                'auth.change_user', 
                'auth.delete_user',
                'auth.view_user',
                'auth.add_group',
                'auth.change_group',
                'auth.view_group',
            ],
            'Gerentes': [
                'auth.add_user',
                'auth.change_user',
                'auth.view_user',
                'auth.view_group',
            ],
            'Operadores': [
                # Permissões operacionais básicas serão adicionadas conforme necessário
            ],
            'Usuários Básicos': [
                # Permissões mínimas, principalmente para visualização do próprio perfil
            ]
        }
        
        created_groups = []
        updated_groups = []
        
        for group_name, permission_codenames in groups_permissions.items():
            # Criar ou obter o grupo
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                created_groups.append(group_name)
                self.stdout.write(
                    self.style.SUCCESS(f'Grupo "{group_name}" criado com sucesso')
                )
            else:
                updated_groups.append(group_name)
                self.stdout.write(
                    self.style.WARNING(f'Grupo "{group_name}" já existe, atualizando permissões...')
                )
            
            # Adicionar permissões ao grupo
            permissions = []
            for codename in permission_codenames:
                try:
                    app_label, codename = codename.split('.')
                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename
                    )
                    permissions.append(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Permissão "{codename}" não encontrada')
                    )
            
            # Definir permissões do grupo
            group.permissions.set(permissions)
            
            self.stdout.write(
                f'  → {len(permissions)} permissões atribuídas ao grupo "{group_name}"'
            )
        
        # Resumo
        self.stdout.write(self.style.SUCCESS('\n=== RESUMO ==='))
        if created_groups:
            self.stdout.write(
                self.style.SUCCESS(f'Grupos criados: {", ".join(created_groups)}')
            )
        if updated_groups:
            self.stdout.write(
                self.style.SUCCESS(f'Grupos atualizados: {", ".join(updated_groups)}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\nGrupos básicos configurados com sucesso!')
        )
