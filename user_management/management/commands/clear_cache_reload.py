"""
Comando para limpar caches e forçar recarga de módulos após correção de bugs.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
import sys


class Command(BaseCommand):
    help = 'Limpa caches e força recarga de módulos após correções de bugs'
    
    def handle(self, *args, **options):
        self.stdout.write("=== LIMPEZA DE CACHE E RECARGA DE MÓDULOS ===\n")
        
        # 1. Limpar cache do Django
        self.stdout.write("1. Limpando cache do Django...")
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("   ✓ Cache limpo com sucesso"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"   ! Erro ao limpar cache: {e}"))
        
        # 2. Recarregar módulos específicos que foram alterados
        self.stdout.write("2. Recarregando módulos alterados...")
        modules_to_reload = [
            'user_management.permission_helpers',
            'user_management.group_views',
            'user_management.views',
        ]
        
        for module_name in modules_to_reload:
            try:
                if module_name in sys.modules:
                    import importlib
                    importlib.reload(sys.modules[module_name])
                    self.stdout.write(f"   ✓ Módulo {module_name} recarregado")
                else:
                    self.stdout.write(f"   - Módulo {module_name} não estava carregado")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"   ! Erro ao recarregar {module_name}: {e}")
                )
        
        # 3. Testar funções críticas
        self.stdout.write("3. Testando funções após recarga...")
        try:
            from django.contrib.auth.models import User
            from user_management.permission_helpers import get_manageable_groups_queryset
            
            # Testar com gerente se existir
            gerente = User.objects.filter(groups__name='Gerentes').first()
            if gerente:
                queryset = get_manageable_groups_queryset(gerente)
                prefetched = queryset.prefetch_related('permissions')
                count = list(prefetched)  # Força execução
                self.stdout.write(
                    self.style.SUCCESS(f"   ✓ Teste de gerente OK: {len(count)} grupos")
                )
            else:
                self.stdout.write("   - Nenhum gerente encontrado para teste")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ✗ Erro no teste: {e}")
            )
            import traceback
            self.stdout.write(traceback.format_exc())
        
        self.stdout.write(f"\n=== LIMPEZA CONCLUÍDA ===")
        self.stdout.write("Recomendações:")
        self.stdout.write("- Reinicie o servidor de desenvolvimento")
        self.stdout.write("- Limpe o cache do navegador (Ctrl+F5)")
        self.stdout.write("- Teste novamente com diferentes usuários")
