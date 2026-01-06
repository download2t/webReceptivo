"""
Comando para criar categorias padrão do sistema
"""
from django.core.management.base import BaseCommand
from servicos.models import Categoria


class Command(BaseCommand):
    help = 'Cria categorias padrão do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Remove todas as categorias existentes antes de criar as novas'
        )

    def handle(self, *args, **options):
        limpar = options['limpar']
        
        # Categorias padrão
        categorias = [
            {'nome': 'Atrativos', 'ordem': 1},
            {'nome': 'Hospedagem', 'ordem': 2},
            {'nome': 'Transporte', 'ordem': 3},
            {'nome': 'Alimentação', 'ordem': 4},
            {'nome': 'Passeios', 'ordem': 5},
            {'nome': 'Eventos', 'ordem': 6},
            {'nome': 'Outros', 'ordem': 99},
        ]
        
        if limpar:
            count = Categoria.objects.count()
            Categoria.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'✓ Removidas {count} categorias existentes\n'))
        
        self.stdout.write(self.style.NOTICE(f'→ Criando {len(categorias)} categorias...\n'))
        
        criadas = 0
        existentes = 0
        
        for cat_data in categorias:
            categoria, created = Categoria.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'ordem': cat_data['ordem'],
                    'ativo': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {categoria.nome}: criada (ordem: {cat_data["ordem"]})'))
                criadas += 1
            else:
                self.stdout.write(f'  - {categoria.nome}: já existe')
                existentes += 1
        
        # Resumo
        self.stdout.write(self.style.NOTICE('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'✓ Criadas: {criadas}'))
        self.stdout.write(self.style.NOTICE(f'→ Já existentes: {existentes}'))
        self.stdout.write(self.style.NOTICE('='*60 + '\n'))
