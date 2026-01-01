"""
Management command para adicionar apenas os serviços que estão faltando
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from servicos.models import Categoria, SubCategoria
from decimal import Decimal


class Command(BaseCommand):
    help = 'Adiciona apenas os serviços que ainda não existem no banco'

    def handle(self, *args, **kwargs):
        self.stdout.write('Adicionando serviços faltantes...\n')
        
        with transaction.atomic():
            # Buscar categoria Atrativos
            try:
                categoria = Categoria.objects.get(nome='Atrativos')
            except Categoria.DoesNotExist:
                categoria = Categoria.objects.create(
                    nome='Atrativos',
                    ordem=1,
                    ativo=True
                )
                self.stdout.write(self.style.SUCCESS('✓ Categoria "Atrativos" criada'))
            
            # Serviços para adicionar (apenas os novos)
            servicos_novos = [
                {
                    'nome': 'TIROLEZA',
                    'valor_inteira': Decimal('94.00'),
                    'valor_meia': Decimal('47.00'),
                    'valor_infantil': Decimal('47.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANCA DE 2 A 11 ANOS, EST.BR, IDOSO, PROF. PR, PCD, DOADOR PR,',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 1,
                    'texto_isencao': 'CRIANÇA ATÉ 1 ANO',
                },
                {
                    'nome': 'MOVIE CARS',
                    'valor_inteira': Decimal('80.00'),
                    'valor_meia': Decimal('40.00'),
                    'valor_infantil': Decimal('40.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANÇA DE 0 A 5 ANOS, IDOSO, PRF. PR, DOADOR PR, PCD, EST. BR',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 4,
                    'texto_isencao': 'CRIANÇA DE 0 A 4 ANOS',
                },
                {
                    'nome': 'SHOW DAS ÁGUAS',
                    'valor_inteira': Decimal('80.00'),
                    'valor_meia': Decimal('40.00'),
                    'valor_infantil': Decimal('40.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANÇA DE 0 A 5 ANOS, IDOSO, PRF. PR, DOADOR PR, PCD, EST. BR',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 4,
                    'texto_isencao': 'CRIANÇA DE 0 A 4 ANOS',
                },
                {
                    'nome': 'SHOW DAS ÁGUAS VIP',
                    'valor_inteira': Decimal('100.00'),
                    'valor_meia': Decimal('50.00'),
                    'valor_infantil': Decimal('50.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANÇA DE 0 A 5 ANOS, IDOSO, PRF. PR, DOADOR PR, PCD, EST. BR R$80,00',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 4,
                    'texto_isencao': 'CRIANÇA DE 0 A 4 ANOS',
                },
                {
                    'nome': 'RAFAIN CHURRASCARIA SHOW',
                    'valor_inteira': Decimal('259.00'),
                    'valor_meia': Decimal('129.50'),
                    'valor_infantil': Decimal('129.50'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANÇA DE 7 A 12 ANOS',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 6,
                    'texto_isencao': 'CRIANÇA DE 0 A 6 ANOS',
                },
                {
                    'nome': 'KATTAMARAM',
                    'valor_inteira': Decimal('240.00'),
                    'valor_meia': Decimal('120.00'),
                    'valor_infantil': Decimal('120.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'IDOSO, ESTUDANTE BR COM CARTEIRINHA, CRIANÇA DE 7 A 11 ANOS, PCD,',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 6,
                    'texto_isencao': 'CRIANÇA DE 0 A 6 ANOS',
                },
                {
                    'nome': 'MACUCO SAFARI',
                    'valor_inteira': Decimal('386.60'),
                    'valor_meia': Decimal('193.30'),
                    'valor_infantil': Decimal('193.30'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'IDOSO, ESTUDANTE BR COM CARTEIRINHA, CRIANÇA DE 7 A 11 ANOS, PCD,',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 6,
                    'texto_isencao': 'CRIANÇA DE 0 A 6 ANOS',
                },
                {
                    'nome': 'IGUASSU SECRET FALLS ALL DAY',
                    'valor_inteira': Decimal('300.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'CRIANÇA DE 0 A 12 ANOS',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 0,
                    'texto_isencao': 'NÃO TEM',
                },
                {
                    'nome': 'IGUASSU SECRET MEIO PERIODO',
                    'valor_inteira': Decimal('200.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'CRIANÇA DE 0 A 12 ANOS',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 0,
                    'texto_isencao': 'NÃO TEM',
                },
                {
                    'nome': 'IGUASSE SECRET TRILHA ÚNICA',
                    'valor_inteira': Decimal('150.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'CRIANÇA DE 0 A 12 ANOS',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 0,
                    'texto_isencao': 'NÃO TEM',
                },
                {
                    'nome': 'LA ARIPUCA',
                    'valor_inteira': Decimal('50.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'NÃO TEM',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 7,
                    'texto_isencao': 'CRIANÇA DE 0 A 7 ANOS',
                },
                {
                    'nome': 'RUINAS SAN IGNACIO',
                    'valor_inteira': Decimal('30.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'NÃO TEM',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 0,
                    'texto_isencao': '',
                },
                {
                    'nome': 'MINAS DE WAND',
                    'valor_inteira': Decimal('30.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'NÃO TEM',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 0,
                    'texto_isencao': '',
                },
                {
                    'nome': 'MESQUITA MULÇUMANA',
                    'valor_inteira': Decimal('30.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'NÃO TEM',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 0,
                    'texto_isencao': '',
                },
            ]
            
            # Adicionar apenas serviços que não existem
            criados = 0
            ja_existentes = 0
            
            for servico_data in servicos_novos:
                existe = SubCategoria.objects.filter(
                    categoria=categoria,
                    nome=servico_data['nome']
                ).exists()
                
                if not existe:
                    SubCategoria.objects.create(
                        categoria=categoria,
                        nome=servico_data['nome'],
                        valor_inteira=servico_data['valor_inteira'],
                        valor_meia=servico_data['valor_meia'],
                        valor_infantil=servico_data['valor_infantil'],
                        aceita_meia_entrada=servico_data['aceita_meia_entrada'],
                        regras_meia_entrada=servico_data['regras_meia_entrada'],
                        permite_infantil=True,  # Permitir infantil por padrão
                        idade_minima_infantil=0,  # Idade mínima infantil padrão
                        idade_maxima_infantil=17,  # Idade máxima infantil padrão
                        possui_isencao=servico_data['idade_isencao_max'] > 0,  # Se tem idade máx > 0, possui isenção
                        idade_isencao_min=servico_data['idade_isencao_min'],
                        idade_isencao_max=servico_data['idade_isencao_max'],
                        texto_isencao=servico_data['texto_isencao'],
                        tem_idade_minima=False,  # Nenhum serviço da lista tem idade mínima
                        idade_minima=0,
                        ativo=True,
                    )
                    criados += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {servico_data["nome"]}'))
                else:
                    ja_existentes += 1
                    self.stdout.write(f'  - {servico_data["nome"]} (já existe)')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Operação concluída!'))
        self.stdout.write(f'  Serviços criados: {criados}')
        self.stdout.write(f'  Serviços já existentes: {ja_existentes}')
        self.stdout.write('='*60 + '\n')
