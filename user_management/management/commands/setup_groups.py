"""
Command para criar os grupos básicos do sistema de permissões.

REGRAS DE PERMISSÕES:
======================

1. ADMINISTRADORES - Controle total do sistema
   - Gerenciar usuários e grupos
   - CRUD completo de todas as entidades
   - Acesso irrestrito ao admin

2. GERENTES - Gestão operacional completa
   - Criar e editar usuários
   - CRUD completo de todas as entidades
   - Visualizar grupos (não pode criar/editar grupos)

3. OPERADORES - Foco em ordens de serviço
   - Apenas VISUALIZAR: Categorias, Serviços, Transfers, Tipos de Meia Entrada
   - NÃO podem editar ou excluir os cadastros acima
   - NÃO podem visualizar usuários
   - CRUD completo de Ordens de Serviço e seus lançamentos

4. USUÁRIOS BÁSICOS - Apenas consulta
   - Apenas VISUALIZAR: Serviços e Ordens de Serviço
   - NÃO podem cadastrar, editar ou excluir nada
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Cria os grupos básicos do sistema de permissões com regras corretas'
    
    def handle(self, *args, **options):
        # Definir grupos e suas permissões
        groups_permissions = {
            'Administradores': [
                # Usuários e grupos - Controle total
                'auth.add_user',
                'auth.change_user', 
                'auth.view_user',
                'auth.add_group',
                'auth.change_group',
                'auth.view_group',
                
                # Categorias - CRUD completo
                'servicos.view_categoria',
                'servicos.add_categoria',
                'servicos.change_categoria',
                'servicos.delete_categoria',
                
                # Serviços (SubCategoria) - CRUD completo
                'servicos.view_subcategoria',
                'servicos.add_subcategoria',
                'servicos.change_subcategoria',
                'servicos.delete_subcategoria',
                
                # Transfers - CRUD completo
                'servicos.view_transfer',
                'servicos.add_transfer',
                'servicos.change_transfer',
                'servicos.delete_transfer',
                
                # Tipos de Meia Entrada - CRUD completo
                'servicos.view_tipomeiaentrada',
                'servicos.add_tipomeiaentrada',
                'servicos.change_tipomeiaentrada',
                'servicos.delete_tipomeiaentrada',
                
                # Ordens de Serviço - CRUD completo
                'servicos.view_ordemservico',
                'servicos.add_ordemservico',
                'servicos.change_ordemservico',
                'servicos.delete_ordemservico',
                
                # Lançamentos de Serviço - CRUD completo
                'servicos.view_lancamentoservico',
                'servicos.add_lancamentoservico',
                'servicos.change_lancamentoservico',
                'servicos.delete_lancamentoservico',
                
                # Transfers OS - CRUD completo
                'servicos.view_transferos',
                'servicos.add_transferos',
                'servicos.change_transferos',
                'servicos.delete_transferos',
            ],
            
            'Gerentes': [
                # Usuários - Pode criar e editar (não pode gerenciar grupos)
                'auth.add_user',
                'auth.change_user',
                'auth.view_user',
                'auth.view_group',  # Apenas visualizar grupos
                
                # Categorias - CRUD completo
                'servicos.view_categoria',
                'servicos.add_categoria',
                'servicos.change_categoria',
                'servicos.delete_categoria',
                
                # Serviços (SubCategoria) - CRUD completo
                'servicos.view_subcategoria',
                'servicos.add_subcategoria',
                'servicos.change_subcategoria',
                'servicos.delete_subcategoria',
                
                # Transfers - CRUD completo
                'servicos.view_transfer',
                'servicos.add_transfer',
                'servicos.change_transfer',
                'servicos.delete_transfer',
                
                # Tipos de Meia Entrada - CRUD completo
                'servicos.view_tipomeiaentrada',
                'servicos.add_tipomeiaentrada',
                'servicos.change_tipomeiaentrada',
                'servicos.delete_tipomeiaentrada',
                
                # Ordens de Serviço - CRUD completo
                'servicos.view_ordemservico',
                'servicos.add_ordemservico',
                'servicos.change_ordemservico',
                'servicos.delete_ordemservico',
                
                # Lançamentos de Serviço - CRUD completo
                'servicos.view_lancamentoservico',
                'servicos.add_lancamentoservico',
                'servicos.change_lancamentoservico',
                'servicos.delete_lancamentoservico',
                
                # Transfers OS - CRUD completo
                'servicos.view_transferos',
                'servicos.add_transferos',
                'servicos.change_transferos',
                'servicos.delete_transferos',
            ],
            
            'Operadores': [
                # NÃO TEM acesso a usuários
                
                # Categorias - APENAS VISUALIZAÇÃO
                'servicos.view_categoria',
                
                # Serviços (SubCategoria) - APENAS VISUALIZAÇÃO
                'servicos.view_subcategoria',
                
                # Transfers - APENAS VISUALIZAÇÃO
                'servicos.view_transfer',
                
                # Tipos de Meia Entrada - APENAS VISUALIZAÇÃO
                'servicos.view_tipomeiaentrada',
                
                # Ordens de Serviço - CRUD COMPLETO
                'servicos.view_ordemservico',
                'servicos.add_ordemservico',
                'servicos.change_ordemservico',
                'servicos.delete_ordemservico',
                
                # Lançamentos de Serviço - CRUD COMPLETO
                'servicos.view_lancamentoservico',
                'servicos.add_lancamentoservico',
                'servicos.change_lancamentoservico',
                'servicos.delete_lancamentoservico',
                
                # Transfers OS - CRUD COMPLETO
                'servicos.view_transferos',
                'servicos.add_transferos',
                'servicos.change_transferos',
                'servicos.delete_transferos',
            ],
            
            'Usuários Básicos': [
                # NÃO TEM acesso a usuários
                # NÃO TEM acesso a cadastros (categorias, transfers, tipos meia)
                
                # Serviços (SubCategoria) - APENAS VISUALIZAÇÃO
                'servicos.view_subcategoria',
                
                # Ordens de Serviço - APENAS VISUALIZAÇÃO
                'servicos.view_ordemservico',
                
                # Lançamentos de Serviço - APENAS VISUALIZAÇÃO
                'servicos.view_lancamentoservico',
                
                # Transfers OS - APENAS VISUALIZAÇÃO
                'servicos.view_transferos',
            ]
        }
        
        self.stdout.write(self.style.NOTICE('\n' + '='*70))
        self.stdout.write(self.style.NOTICE('CONFIGURANDO GRUPOS DE PERMISSÕES'))
        self.stdout.write(self.style.NOTICE('='*70 + '\n'))
        
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
            
            total_permissions_added += len(permissions)
            self.stdout.write('')  # Linha em branco
        
        # Resumo final
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✨ RESUMO FINAL'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        if created_groups:
            self.stdout.write(
                self.style.SUCCESS(f'🆕 Grupos criados: {", ".join(created_groups)}')
            )
        if updated_groups:
            self.stdout.write(
                self.style.WARNING(f'🔄 Grupos atualizados: {", ".join(updated_groups)}')
            )
        
        self.stdout.write(f'🔑 Total de permissões configuradas: {total_permissions_added}')
        
        # Tabela de resumo de permissões
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.NOTICE('📋 REGRAS DE PERMISSÕES POR GRUPO:'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        self.stdout.write(self.style.SUCCESS('\n🔷 ADMINISTRADORES:'))
        self.stdout.write('   ✅ Usuários e Grupos (CRUD completo)')
        self.stdout.write('   ✅ Categorias (CRUD completo)')
        self.stdout.write('   ✅ Serviços (CRUD completo)')
        self.stdout.write('   ✅ Transfers (CRUD completo)')
        self.stdout.write('   ✅ Tipos de Meia Entrada (CRUD completo)')
        self.stdout.write('   ✅ Ordens de Serviço (CRUD completo)')
        
        self.stdout.write(self.style.WARNING('\n🔶 GERENTES:'))
        self.stdout.write('   ✅ Usuários (criar, editar, visualizar)')
        self.stdout.write('   ✅ Grupos (apenas visualizar)')
        self.stdout.write('   ✅ Categorias (CRUD completo)')
        self.stdout.write('   ✅ Serviços (CRUD completo)')
        self.stdout.write('   ✅ Transfers (CRUD completo)')
        self.stdout.write('   ✅ Tipos de Meia Entrada (CRUD completo)')
        self.stdout.write('   ✅ Ordens de Serviço (CRUD completo)')
        
        self.stdout.write(self.style.NOTICE('\n🔹 OPERADORES:'))
        self.stdout.write('   ❌ Usuários (SEM ACESSO)')
        self.stdout.write('   👁️  Categorias (apenas visualizar)')
        self.stdout.write('   👁️  Serviços (apenas visualizar)')
        self.stdout.write('   👁️  Transfers (apenas visualizar)')
        self.stdout.write('   👁️  Tipos de Meia Entrada (apenas visualizar)')
        self.stdout.write('   ✅ Ordens de Serviço (CRUD completo)')
        
        self.stdout.write(self.style.NOTICE('\n🔘 USUÁRIOS BÁSICOS:'))
        self.stdout.write('   ❌ Usuários (SEM ACESSO)')
        self.stdout.write('   ❌ Categorias (SEM ACESSO)')
        self.stdout.write('   ❌ Transfers (SEM ACESSO)')
        self.stdout.write('   ❌ Tipos de Meia Entrada (SEM ACESSO)')
        self.stdout.write('   👁️  Serviços (apenas visualizar)')
        self.stdout.write('   👁️  Ordens de Serviço (apenas visualizar)')
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✅ Configuração de grupos concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
