"""
Comando para limpar todos os dados do app servicos
"""
from django.core.management.base import BaseCommand
from servicos.models import Categoria, SubCategoria, TipoMeiaEntrada, LancamentoServico


class Command(BaseCommand):
    help = 'Remove todos os dados de serviços, categorias, tipos de meia entrada e lançamentos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a exclusão de todos os dados',
        )

    def handle(self, *args, **options):
        if not options['confirmar']:
            self.stdout.write(self.style.ERROR('ATENÇÃO: Esta operação irá deletar TODOS os dados de serviços!'))
            self.stdout.write(self.style.WARNING('Para confirmar, execute: python manage.py limpar_servicos --confirmar'))
            return
        
        self.stdout.write(self.style.WARNING('Iniciando limpeza de dados...'))
        
        # Contar registros antes
        total_lancamentos = LancamentoServico.objects.count()
        total_servicos = SubCategoria.objects.count()
        total_categorias = Categoria.objects.count()
        total_tipos_meia = TipoMeiaEntrada.objects.count()
        
        self.stdout.write(f'\nDados a serem removidos:')
        self.stdout.write(f'  - {total_lancamentos} lançamentos de serviço')
        self.stdout.write(f'  - {total_servicos} serviços')
        self.stdout.write(f'  - {total_categorias} categorias')
        self.stdout.write(f'  - {total_tipos_meia} tipos de meia entrada')
        
        # Deletar na ordem correta (das dependências para as tabelas principais)
        self.stdout.write('\n1. Removendo lançamentos de serviço...')
        LancamentoServico.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'   ✓ {total_lancamentos} lançamentos removidos'))
        
        self.stdout.write('2. Removendo serviços (subcategorias)...')
        SubCategoria.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'   ✓ {total_servicos} serviços removidos'))
        
        self.stdout.write('3. Removendo categorias...')
        Categoria.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'   ✓ {total_categorias} categorias removidas'))
        
        self.stdout.write('4. Removendo tipos de meia entrada...')
        TipoMeiaEntrada.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'   ✓ {total_tipos_meia} tipos de meia entrada removidos'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Limpeza concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS('Banco de dados de serviços zerado.'))
