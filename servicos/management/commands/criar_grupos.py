"""
Management command para criar grupos de permissões padrão.

Uso:
    python manage.py criar_grupos
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from servicos.permissions import GRUPOS_PERMISSOES


class Command(BaseCommand):
    help = 'Cria grupos de permissões padrão para o sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n🔧 Atualizando grupos de permissões existentes...\n'))
        
        # Primeiro, excluir grupos temporários se existirem
        grupos_antigos = ['Operador', 'Coordenador', 'Gestor de Cadastros', 'Gerente']
        for nome in grupos_antigos:
            try:
                grupo = Group.objects.get(name=nome)
                grupo.delete()
                self.stdout.write(self.style.SUCCESS(f'🗑️  Grupo temporário "{nome}" removido'))
            except Group.DoesNotExist:
                pass
        
        self.stdout.write('')
        
        grupos_criados = 0
        grupos_atualizados = 0
        permissoes_adicionadas = 0
        
        for nome_grupo, config in GRUPOS_PERMISSOES.items():
            # Cria ou obtém o grupo
            grupo, created = Group.objects.get_or_create(name=nome_grupo)
            
            if created:
                grupos_criados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Grupo "{nome_grupo}" criado')
                )
            else:
                grupos_atualizados += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Atualizando grupo "{nome_grupo}"...')
                )
            
            # NÃO limpa permissões existentes - apenas adiciona as novas
            perms_antes = grupo.permissions.count()
            
            # Adiciona permissões
            perms_adicionadas = 0
            for perm_string in config['permissoes']:
                app_label, codename = perm_string.split('.')
                
                try:
                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename
                    )
                    # Adiciona apenas se ainda não tiver
                    if not grupo.permissions.filter(pk=permission.pk).exists():
                        grupo.permissions.add(permission)
                        perms_adicionadas += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'   ⚠️  Permissão não encontrada: {perm_string}')
                    )
            
            perms_depois = grupo.permissions.count()
            permissoes_adicionadas += perms_adicionadas
            
            if perms_adicionadas > 0:
                self.stdout.write(f'   ➕ {perms_adicionadas} novas permissões adicionadas ({perms_antes} → {perms_depois})')
            else:
                self.stdout.write(f'   ✓ Nenhuma permissão nova (já tem {perms_depois})')
            self.stdout.write(f'   ℹ️  {config["descricao"]}\n')
        
        # Resumo
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✨ RESUMO:'))
        self.stdout.write(f'   🆕 Grupos criados: {grupos_criados}')
        self.stdout.write(f'   🔄 Grupos atualizados: {grupos_atualizados}')
        self.stdout.write(f'   🔑 Total de permissões configuradas: {permissoes_adicionadas}')
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # Instruções
        self.stdout.write(self.style.WARNING('📚 GRUPOS ATUALIZADOS:'))
        self.stdout.write('   ✅ Administradores - Controle total (usuários + serviços)')
        self.stdout.write('   ✅ Gerentes - Gestão de usuários + CRUD completo de serviços')
        self.stdout.write('   ✅ Operadores - CRUD de Ordens de Serviço + visualizar cadastros')
        self.stdout.write('   ✅ Usuários Básicos - Apenas visualização')
        self.stdout.write('\n   💡 As permissões antigas foram PRESERVADAS')
        self.stdout.write('   💡 Novas permissões de serviços foram ADICIONADAS\n')
