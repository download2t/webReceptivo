"""
Comando para importar serviços de Foz do Iguaçu
"""
import json
from decimal import Decimal
from pathlib import Path
from django.core.management.base import BaseCommand
from servicos.models import Categoria, SubCategoria


class Command(BaseCommand):
    help = 'Importa serviços turísticos de Foz do Iguaçu'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categoria',
            type=str,
            default='Atrativos',
            help='Nome da categoria para os serviços (padrão: Atrativos)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Atualizar serviços existentes (padrão: apenas criar novos)'
        )

    def handle(self, *args, **options):
        categoria_nome = options['categoria']
        update_existing = options['update']
        
        # Obter ou criar a categoria
        categoria, created = Categoria.objects.get_or_create(
            nome=categoria_nome,
            defaults={
                'ativo': True,
                'ordem': 1
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Categoria "{categoria_nome}" criada'))
        else:
            self.stdout.write(self.style.WARNING(f'→ Categoria "{categoria_nome}" já existe'))
        
        # Carregar dados do JSON
        json_path = Path(__file__).parent.parent.parent / 'fixtures' / 'servicos_foz.json'
        
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f'✗ Arquivo não encontrado: {json_path}'))
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            servicos_data = json.load(f)
        
        self.stdout.write(self.style.NOTICE(f'\n→ Carregados {len(servicos_data)} serviços do arquivo\n'))
        
        # Contadores
        criados = 0
        atualizados = 0
        ignorados = 0
        
        # Importar cada serviço
        for data in servicos_data:
            nome = data['nome']
            
            # Verificar se já existe
            existing = SubCategoria.objects.filter(nome=nome, categoria=categoria).first()
            
            if existing and not update_existing:
                self.stdout.write(f'  - {nome}: já existe (use --update para atualizar)')
                ignorados += 1
                continue
            
            # Preparar dados do serviço
            servico_data = {
                'categoria': categoria,
                'nome': nome,
                'valor_inteira': Decimal(str(data['valor_inteira'])),
                'valor_meia': Decimal(str(data['valor_meia'])),
                'valor_infantil': Decimal(str(data['valor_infantil'])),
                'aceita_meia_entrada': data['aceita_meia_entrada'],
                'regras_meia_entrada': data['regras_meia'],
                'possui_isencao': data['possui_isencao'],
                'texto_isencao': data['regras_isencao'],
                'permite_infantil': data['permite_infantil'],
                'tem_idade_minima': data['tem_idade_minima'],
                'ativo': True
            }
            
            # Campos opcionais (podem ser None)
            if data.get('idade_minima') is not None:
                servico_data['idade_minima'] = data['idade_minima']
            
            if data.get('idade_minima_infantil') is not None:
                servico_data['idade_minima_infantil'] = data['idade_minima_infantil']
            else:
                servico_data['idade_minima_infantil'] = 0
            
            if data.get('idade_maxima_infantil') is not None:
                servico_data['idade_maxima_infantil'] = data['idade_maxima_infantil']
            else:
                servico_data['idade_maxima_infantil'] = 17
            
            # Campos de isenção por idade
            servico_data['idade_isencao_min'] = 0
            servico_data['idade_isencao_max'] = 0
            
            # Se possui isenção, tentar extrair idades do texto
            if data['possui_isencao'] and data['regras_isencao']:
                texto = data['regras_isencao'].upper()
                # Tentar extrair idades do texto (ex: "CRIANÇA DE 0 A 6 ANOS")
                import re
                match = re.search(r'(\d+)\s*A\s*(\d+)', texto)
                if match:
                    servico_data['idade_isencao_min'] = int(match.group(1))
                    servico_data['idade_isencao_max'] = int(match.group(2))
            
            # Criar ou atualizar
            if existing:
                for key, value in servico_data.items():
                    setattr(existing, key, value)
                existing.save()
                self.stdout.write(self.style.WARNING(f'  ✓ {nome}: atualizado'))
                atualizados += 1
            else:
                SubCategoria.objects.create(**servico_data)
                self.stdout.write(self.style.SUCCESS(f'  ✓ {nome}: criado'))
                criados += 1
        
        # Resumo
        self.stdout.write(self.style.NOTICE('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'✓ Criados: {criados}'))
        if update_existing:
            self.stdout.write(self.style.WARNING(f'✓ Atualizados: {atualizados}'))
        self.stdout.write(self.style.NOTICE(f'→ Ignorados: {ignorados}'))
        self.stdout.write(self.style.NOTICE('='*60 + '\n'))
        
        if not update_existing and ignorados > 0:
            self.stdout.write(
                self.style.WARNING('Dica: Use --update para atualizar serviços existentes\n')
            )
