"""
Management command para popular serviços com dados reais dos atrativos
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from servicos.models import Categoria, SubCategoria, TipoMeiaEntrada
from decimal import Decimal


class Command(BaseCommand):
    help = 'Popula o banco com serviços turísticos reais'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando população de serviços...\n')
        
        with transaction.atomic():
            # Criar categoria Atrativos
            categoria, created = Categoria.objects.get_or_create(
                nome='Atrativos',
                defaults={'ordem': 1, 'ativo': True}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Categoria "Atrativos" criada'))
            else:
                self.stdout.write('  Categoria "Atrativos" já existe')
            
            # Serviços para criar
            servicos = [
                {
                    'nome': 'CATARATAS BR',
                    'valor_inteira': Decimal('105.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'NÃO ACEITA MEIA ENTRADA',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 6,
                    'texto_isencao': 'CRIANÇA DE 0 A 6 ANOS',
                },
                {
                    'nome': 'PARQUE DAS AVES',
                    'valor_inteira': Decimal('90.00'),
                    'valor_meia': Decimal('45.00'),
                    'valor_infantil': Decimal('45.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'EST. DE 9 A 16 ANOS COM RG, EST. COM CARTEIRINHA, PROF BR, IDOSO, DOADOR DE SANGUE, POL.BR, PCD E ACOM.',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 8,
                    'texto_isencao': 'CRIANÇA DE 0 A 8 ANOS',
                },
                {
                    'nome': 'ITAIPU PANORAMICA',
                    'valor_inteira': Decimal('60.00'),
                    'valor_meia': Decimal('30.00'),
                    'valor_infantil': Decimal('30.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIAN. 6 A 11ANOS, IDOSO, EST. BR, PROF. BR, DOADOR DE SANGUE, PCD, PES.COM CANCER.',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 5,
                    'texto_isencao': 'CRIANÇA DE 0 A 5 ANOS',
                },
                {
                    'nome': 'ITAIPU ESPECIAL',
                    'valor_inteira': Decimal('105.00'),
                    'valor_meia': Decimal('82.50'),
                    'valor_infantil': Decimal('82.50'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'IDOSO, EST. BR, PROF. BR, PCD, DOADOR DE SANGUE, PCD, PES.COM CANCER.',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 5,
                    'texto_isencao': 'PASSEIO APENAS CRIANÇA ACIMA DE 14 ANOS',
                },
                {
                    'nome': 'REFÚGIO BIOLÓGICO',
                    'valor_inteira': Decimal('42.00'),
                    'valor_meia': Decimal('21.00'),
                    'valor_infantil': Decimal('21.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANCA DE 6 A 11 ANOS, IDOSO, EST. BR, PROF. BR, DOADOR DE SANGUE, PCD, PES.COM CANCER.',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 5,
                    'texto_isencao': 'CRIANÇA DE 0 A 5 ANOS',
                },
                {
                    'nome': 'ILUMINADA ESPECIAL',
                    'valor_inteira': Decimal('150.00'),
                    'valor_meia': Decimal('75.00'),
                    'valor_infantil': Decimal('75.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANCA DE 6 A 11 ANOS, IDOSO, EST. BR, PROF. BR, DOADOR DE SANGUE, PCD, PES.COM CANCER.',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 5,
                    'texto_isencao': 'CRIANÇA DE 0 A 5 ANOS',
                },
                {
                    'nome': 'ILUMINADA',
                    'valor_inteira': Decimal('48.00'),
                    'valor_meia': Decimal('24.00'),
                    'valor_infantil': Decimal('24.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANCA DE 6 A 11 ANOS, IDOSO, EST. BR, PROF. BR, DOADOR DE SANGUE, PCD, PES.COM CANCER.',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 5,
                    'texto_isencao': 'CRIANÇA DE 0 A 5 ANOS',
                },
                {
                    'nome': 'MARCO DAS TRÊS FRONTEIRAS',
                    'valor_inteira': Decimal('49.00'),
                    'valor_meia': Decimal('24.50'),
                    'valor_infantil': Decimal('24.50'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'IDOSO, ESTUDANTE COM CARTEIRINHA, CRIANCA DE 6 A 11 ANOS R$26,00',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 5,
                    'texto_isencao': 'CRIANÇA DE 0 A 5 ANOS',
                },
                {
                    'nome': 'RODA GIGANTE',
                    'valor_inteira': Decimal('70.80'),
                    'valor_meia': Decimal('35.00'),
                    'valor_infantil': Decimal('35.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANCA DE 0 A 4 ANOS R$40,00 -',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 3,
                    'texto_isencao': 'CRIANÇA DE 0 A 3 ANOS',
                },
                {
                    'nome': 'DREAMLAND COMBO 6',
                    'valor_inteira': Decimal('250.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'NÃO TEM',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 0,
                    'texto_isencao': '',
                },
                {
                    'nome': 'DREAMLAND COMBO 5',
                    'valor_inteira': Decimal('220.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'NÃO TEM',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 0,
                    'texto_isencao': '',
                },
                {
                    'nome': 'DREAMLAND QUARTETO',
                    'valor_inteira': Decimal('190.00'),
                    'valor_meia': Decimal('0.00'),
                    'valor_infantil': Decimal('0.00'),
                    'aceita_meia_entrada': False,
                    'regras_meia_entrada': 'NÃO TEM',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 0,
                    'texto_isencao': '',
                },
                {
                    'nome': 'DREAMLAND TRIO NATUREZA',
                    'valor_inteira': Decimal('165.00'),
                    'valor_meia': Decimal('82.50'),
                    'valor_infantil': Decimal('82.50'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'DINO, TIROLEZA, ECO PARK',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 1,
                    'texto_isencao': 'CRIANÇA ATÉ 1 ANO',
                },
                {
                    'nome': 'TRIO BY NIGHT',
                    'valor_inteira': Decimal('165.00'),
                    'valor_meia': Decimal('82.50'),
                    'valor_infantil': Decimal('82.50'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CERA,ICE, MOTOR',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 1,
                    'texto_isencao': 'CRIANÇA ATÉ 1 ANO',
                },
                {
                    'nome': 'TRIO AVENTURA',
                    'valor_inteira': Decimal('165.00'),
                    'valor_meia': Decimal('82.50'),
                    'valor_infantil': Decimal('82.50'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'MUSEU, DINOLHAS, DINO',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 1,
                    'texto_isencao': 'CRIANÇA ATÉ 1 ANO',
                },
                {
                    'nome': 'MUSEU, MARA, ICE, MOTOR',
                    'valor_inteira': Decimal('99.00'),
                    'valor_meia': Decimal('49.50'),
                    'valor_infantil': Decimal('49.50'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANCA DE 2 A 11 ANOS, EST.BR, IDOSO, PROF. PR, PCD, DOADOR PR,',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 1,
                    'texto_isencao': 'CRIANÇA ATÉ 1 ANO',
                },
                {
                    'nome': 'DREAM ECO PARK',
                    'valor_inteira': Decimal('70.00'),
                    'valor_meia': Decimal('35.00'),
                    'valor_infantil': Decimal('35.00'),
                    'aceita_meia_entrada': True,
                    'regras_meia_entrada': 'CRIANCA DE 2 A 11 ANOS, EST.BR, IDOSO, PROF. PR, PCD, DOADOR PR,',
                    'idade_isencao_min': 0,
                    'idade_isencao_max': 1,
                    'texto_isencao': 'CRIANÇA ATÉ 1 ANO',
                },
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
                    'nome': 'SHOW DAS ÁGUAS',
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
            
            # Criar serviços
            criados = 0
            atualizados = 0
            
            for servico_data in servicos:
                servico, created = SubCategoria.objects.update_or_create(
                    categoria=categoria,
                    nome=servico_data['nome'],
                    defaults={
                        'valor_inteira': servico_data['valor_inteira'],
                        'valor_meia': servico_data['valor_meia'],
                        'valor_infantil': servico_data['valor_infantil'],
                        'aceita_meia_entrada': servico_data['aceita_meia_entrada'],
                        'regras_meia_entrada': servico_data['regras_meia_entrada'],
                        'idade_isencao_min': servico_data['idade_isencao_min'],
                        'idade_isencao_max': servico_data['idade_isencao_max'],
                        'texto_isencao': servico_data['texto_isencao'],
                        'ativo': True,
                    }
                )
                
                if created:
                    criados += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {servico.nome}'))
                else:
                    atualizados += 1
                    self.stdout.write(f'  ↻ {servico.nome} (atualizado)')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ População concluída!'))
        self.stdout.write(f'  Serviços criados: {criados}')
        self.stdout.write(f'  Serviços atualizados: {atualizados}')
        self.stdout.write('='*60 + '\n')
