"""
Comando para criar tipos de meia entrada padrão
"""
from django.core.management.base import BaseCommand
from servicos.models import TipoMeiaEntrada


class Command(BaseCommand):
    help = 'Cria tipos de meia entrada padrão (PCD, Idoso, Estudante, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Remove todos os tipos existentes antes de criar os novos'
        )

    def handle(self, *args, **options):
        limpar = options['limpar']
        
        # Tipos de meia entrada padrão
        tipos = [
            {
                'nome': 'PCD',
                'descricao': 'Pessoa com Deficiência - Apresentar documentação comprobatória'
            },
            {
                'nome': 'DOADOR DE SANGUE',
                'descricao': 'Doador de sangue regular - Apresentar carteirinha de doador'
            },
            {
                'nome': 'IDOSO',
                'descricao': 'Pessoa idosa conforme legislação vigente - Apresentar documento de identificação'
            },
            {
                'nome': 'ESTUDANTE BR',
                'descricao': 'Estudante brasileiro - Apresentar carteirinha estudantil válida'
            },
            {
                'nome': 'ESTUDANTE BR COM CARTEIRINHA',
                'descricao': 'Estudante brasileiro com carteirinha de identificação estudantil válida'
            },
            {
                'nome': 'PROFESSOR BR',
                'descricao': 'Professor brasileiro - Apresentar documentação comprobatória'
            },
            {
                'nome': 'POLICIAL BR',
                'descricao': 'Policial brasileiro - Apresentar documentação funcional'
            },
            {
                'nome': 'ACOMPANHANTE DE PCD',
                'descricao': 'Acompanhante de pessoa com deficiência'
            },
            {
                'nome': 'PESSOA COM CANCER',
                'descricao': 'Pessoa em tratamento oncológico - Apresentar documentação médica'
            },
            {
                'nome': 'CRIANÇA',
                'descricao': 'Criança conforme faixa etária especificada no serviço'
            },
            {
                'nome': 'ADOLESCENTE',
                'descricao': 'Adolescente conforme faixa etária especificada no serviço'
            },
            {
                'nome': 'JOVEM',
                'descricao': 'Jovem conforme faixa etária especificada no serviço'
            },
        ]
        
        if limpar:
            count = TipoMeiaEntrada.objects.count()
            TipoMeiaEntrada.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'✓ Removidos {count} tipos existentes\n'))
        
        self.stdout.write(self.style.NOTICE(f'→ Criando {len(tipos)} tipos de meia entrada...\n'))
        
        criados = 0
        existentes = 0
        
        for tipo_data in tipos:
            tipo, created = TipoMeiaEntrada.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults={
                    'descricao': tipo_data['descricao'],
                    'ativo': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {tipo.nome}: criado'))
                criados += 1
            else:
                self.stdout.write(f'  - {tipo.nome}: já existe')
                existentes += 1
        
        # Resumo
        self.stdout.write(self.style.NOTICE('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'✓ Criados: {criados}'))
        self.stdout.write(self.style.NOTICE(f'→ Já existentes: {existentes}'))
        self.stdout.write(self.style.NOTICE('='*60 + '\n'))
