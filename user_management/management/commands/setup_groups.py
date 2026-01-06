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
                # Permissões de usuários e grupos
                'auth.add_user',
                'auth.change_user', 
                # 'auth.delete_user',  # REMOVIDO: Apenas inativação permitida
                'auth.view_user',
                'auth.add_group',
                'auth.change_group',
                'auth.view_group',
                
                # Módulo de Serviços - Acesso completo
                'servicos.view_categoria',
                'servicos.add_categoria',
                'servicos.change_categoria',
                'servicos.delete_categoria',
                
                'servicos.view_subcategoria',
                'servicos.add_subcategoria',
                'servicos.change_subcategoria',
                'servicos.delete_subcategoria',
                
                'servicos.view_transfer',
                'servicos.add_transfer',
                'servicos.change_transfer',
                'servicos.delete_transfer',
                
                'servicos.view_tipomeiaentrada',
                'servicos.add_tipomeiaentrada',
                'servicos.change_tipomeiaentrada',
                'servicos.delete_tipomeiaentrada',
                
                'servicos.view_ordemservico',
                'servicos.add_ordemservico',
                'servicos.change_ordemservico',
                'servicos.delete_ordemservico',
                
                'servicos.view_lancamentoservico',
                'servicos.add_lancamentoservico',
                'servicos.change_lancamentoservico',
                'servicos.delete_lancamentoservico',
                
                'servicos.view_transferos',
                'servicos.add_transferos',
                'servicos.change_transferos',
                'servicos.delete_transferos',
            ],
            'Gerentes': [
                # Permissões de usuários
                'auth.add_user',
                'auth.change_user',
                'auth.view_user',
                'auth.view_group',
                
                # Módulo de Serviços - Acesso completo (TODOS OS PODERES)
                'servicos.view_categoria',
                'servicos.add_categoria',
                'servicos.change_categoria',
                'servicos.delete_categoria',
                
                'servicos.view_subcategoria',
                'servicos.add_subcategoria',
                'servicos.change_subcategoria',
                'servicos.delete_subcategoria',
                
                'servicos.view_transfer',
                'servicos.add_transfer',
                'servicos.change_transfer',
                'servicos.delete_transfer',
                
                'servicos.view_tipomeiaentrada',
                'servicos.add_tipomeiaentrada',
                'servicos.change_tipomeiaentrada',
                'servicos.delete_tipomeiaentrada',
                
                'servicos.view_ordemservico',
                'servicos.add_ordemservico',
                'servicos.change_ordemservico',
                'servicos.delete_ordemservico',
                
                'servicos.view_lancamentoservico',
                'servicos.add_lancamentoservico',
                'servicos.change_lancamentoservico',
                'servicos.delete_lancamentoservico',
                
                'servicos.view_transferos',
                'servicos.add_transferos',
                'servicos.change_transferos',
                'servicos.delete_transferos',
            ],
            'Operadores': [
                # Visualização de cadastros
                'servicos.view_categoria',
                'servicos.view_subcategoria',
                'servicos.view_transfer',
                'servicos.view_tipomeiaentrada',
                
                # CRUD completo de Ordens de Serviço
                'servicos.view_ordemservico',
                'servicos.add_ordemservico',
                'servicos.change_ordemservico',
                'servicos.delete_ordemservico',
                
                'servicos.view_lancamentoservico',
                'servicos.add_lancamentoservico',
                'servicos.change_lancamentoservico',
                'servicos.delete_lancamentoservico',
                
                'servicos.view_transferos',
                'servicos.add_transferos',
                'servicos.change_transferos',
                'servicos.delete_transferos',
            ],
            'Usuários Básicos': [
                # Apenas visualização
                'servicos.view_categoria',
                'servicos.view_subcategoria',
                'servicos.view_transfer',
                'servicos.view_tipomeiaentrada',
                'servicos.view_ordemservico',
                'servicos.view_lancamentoservico',
                'servicos.view_transferos',
            ]
        }
        
        created_groups = []
        updated_groups = []
        total_permissions_added = 0
        
        for group_name, permission_codenames in groups_permissions.items():
            # Criar ou obter o grupo
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                created_groups.append(group_name)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Grupo "{group_name}" criado com sucesso')
                )
            else:
                updated_groups.append(group_name)
                self.stdout.write(
                    self.style.WARNING(f'🔄 Grupo "{group_name}" já existe, atualizando permissões...')
                )
                perms_antes = group.permissions.count()
            
            # Coletar permissões
            permissions = []
            permissions_not_found = []
            
            for perm_string in permission_codenames:
                try:
                    app_label, codename = perm_string.split('.')
                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename
                    )
                    permissions.append(permission)
                except Permission.DoesNotExist:
                    permissions_not_found.append(perm_string)
                    self.stdout.write(
                        self.style.WARNING(f'   ⚠️  Permissão "{perm_string}" não encontrada')
                    )
            
            # Atribuir permissões ao grupo
            group.permissions.set(permissions)
            perms_depois = group.permissions.count()
            
            # Mostrar resultado
            if created:
                self.stdout.write(f'   ➕ {len(permissions)} permissões adicionadas')
            else:
                diff = perms_depois - perms_antes
                if diff > 0:
                    self.stdout.write(f'   📈 {perms_antes} → {perms_depois} permissões (+{diff})')
                elif diff < 0:
                    self.stdout.write(f'   📉 {perms_antes} → {perms_depois} permissões ({diff})')
                else:
                    self.stdout.write(f'   ✓ {perms_depois} permissões (sem mudanças)')
            
            if permissions_not_found:
                self.stdout.write(
                    self.style.WARNING(f'   ⚠️  {len(permissions_not_found)} permissões não encontradas')
                )
            
            self.stdout.write('')  # Linha em branco
        
        # Resumo
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('✨ RESUMO:'))
        
        if created_groups:
            self.stdout.write(
                self.style.SUCCESS(f'   🆕 Grupos criados: {", ".join(created_groups)}')
            )
        if updated_groups:
            self.stdout.write(
                self.style.SUCCESS(f'   🔄 Grupos atualizados: {", ".join(updated_groups)}')
            )
        
        self.stdout.write(f'   🔑 Total de permissões configuradas: {total_permissions_added}')
        self.stdout.write(self.style.SUCCESS('='*60))
        
        # Informações sobre Gerentes
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📚 PERMISSÕES DOS GERENTES:'))
        self.stdout.write('   ✅ Gestão de usuários (add, change, view)')
        self.stdout.write('   ✅ Ordens de Serviço (CRUD completo)')
        self.stdout.write('   ✅ Categorias (CRUD completo)')
        self.stdout.write('   ✅ Serviços (CRUD completo)')
        self.stdout.write('   ✅ Transfers (CRUD completo)')
        self.stdout.write('   ✅ Meia Entrada (CRUD completo)')
        self.stdout.write('')
        
        if created_groups:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Grupos criados: {", ".join(created_groups)}')
            )
        if updated_groups:
            self.stdout.write(
                self.style.SUCCESS(f'Grupos atualizados: {", ".join(updated_groups)}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\nGrupos básicos configurados com sucesso!')
        )
