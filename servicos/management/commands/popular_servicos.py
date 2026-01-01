"""
Comando para popular dados iniciais de exemplo no app servicos
"""
from django.core.management.base import BaseCommand
from servicos.models import Categoria, SubCategoria, TipoMeiaEntrada


class Command(BaseCommand):
    help = 'Popula dados de exemplo para o app servicos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando população de dados...'))
        
        # Criar Tipos de Meia Entrada
        self.stdout.write('Criando tipos de meia entrada...')
        tipos_meia = [
            {'nome': 'Estudante', 'descricao': 'Estudante com carteirinha válida'},
            {'nome': 'Idoso', 'descricao': 'Pessoa com 60 anos ou mais'},
            {'nome': 'PCD', 'descricao': 'Pessoa com Deficiência'},
            {'nome': 'Professores', 'descricao': 'Professores com documento válido'},
        ]
        
        for tipo_data in tipos_meia:
            tipo, created = TipoMeiaEntrada.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults={'descricao': tipo_data['descricao']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Criado: {tipo.nome}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - Já existe: {tipo.nome}'))
        
        # Criar Categorias
        self.stdout.write('\nCriando categorias...')
        categorias_data = [
            {'nome': 'Atrativos Turísticos', 'ordem': 1},
            {'nome': 'Hospedagem', 'ordem': 2},
            {'nome': 'Alimentação', 'ordem': 3},
            {'nome': 'Transporte', 'ordem': 4},
            {'nome': 'Passeios', 'ordem': 5},
        ]
        
        categorias = {}
        for cat_data in categorias_data:
            categoria, created = Categoria.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={'ordem': cat_data['ordem']}
            )
            categorias[cat_data['nome']] = categoria
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Criado: {categoria.nome}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - Já existe: {categoria.nome}'))
        
        # Criar Subcategorias (Serviços)
        self.stdout.write('\nCriando serviços...')
        servicos_data = [
            # Atrativos Turísticos
            {
                'categoria': 'Atrativos Turísticos',
                'nome': 'Cristo Redentor',
                'descricao': 'Ingresso para o Cristo Redentor com transporte incluso',
                'valor_inteira': 120.00,
                'valor_meia': 60.00,
                'valor_infantil': 40.00
            },
            {
                'categoria': 'Atrativos Turísticos',
                'nome': 'Pão de Açúcar',
                'descricao': 'Bondinho do Pão de Açúcar - ida e volta',
                'valor_inteira': 150.00,
                'valor_meia': 75.00,
                'valor_infantil': 50.00
            },
            {
                'categoria': 'Atrativos Turísticos',
                'nome': 'AquaRio',
                'descricao': 'Maior aquário marinho da América do Sul',
                'valor_inteira': 100.00,
                'valor_meia': 50.00,
                'valor_infantil': 30.00
            },
            
            # Passeios
            {
                'categoria': 'Passeios',
                'nome': 'City Tour Rio de Janeiro',
                'descricao': 'Tour completo pelos principais pontos turísticos da cidade',
                'valor_inteira': 200.00,
                'valor_meia': 100.00,
                'valor_infantil': 80.00
            },
            {
                'categoria': 'Passeios',
                'nome': 'Passeio de Escuna',
                'descricao': 'Volta às ilhas com paradas para mergulho',
                'valor_inteira': 180.00,
                'valor_meia': 90.00,
                'valor_infantil': 70.00
            },
            
            # Hospedagem
            {
                'categoria': 'Hospedagem',
                'nome': 'Hotel Copacabana - Diária Simples',
                'descricao': 'Quarto standard com café da manhã',
                'valor_inteira': 350.00,
                'valor_meia': 175.00,
                'valor_infantil': 100.00
            },
            {
                'categoria': 'Hospedagem',
                'nome': 'Pousada Ipanema - Diária Dupla',
                'descricao': 'Quarto duplo com café da manhã',
                'valor_inteira': 500.00,
                'valor_meia': 250.00,
                'valor_infantil': 150.00
            },
            
            # Alimentação
            {
                'categoria': 'Alimentação',
                'nome': 'Churrascaria Rodízio',
                'descricao': 'Rodízio completo de carnes com buffet',
                'valor_inteira': 90.00,
                'valor_meia': 45.00,
                'valor_infantil': 30.00
            },
            {
                'categoria': 'Alimentação',
                'nome': 'Restaurante Frutos do Mar',
                'descricao': 'Almoço ou jantar com frutos do mar',
                'valor_inteira': 120.00,
                'valor_meia': 60.00,
                'valor_infantil': 40.00
            },
            
            # Transporte
            {
                'categoria': 'Transporte',
                'nome': 'Transfer Aeroporto - Hotel',
                'descricao': 'Transporte privativo do aeroporto para o hotel',
                'valor_inteira': 150.00,
                'valor_meia': 75.00,
                'valor_infantil': 50.00
            },
        ]
        
        for servico_data in servicos_data:
            categoria_nome = servico_data.pop('categoria')
            categoria = categorias[categoria_nome]
            
            servico, created = SubCategoria.objects.get_or_create(
                categoria=categoria,
                nome=servico_data['nome'],
                defaults={
                    'descricao': servico_data['descricao'],
                    'valor_inteira': servico_data['valor_inteira'],
                    'valor_meia': servico_data['valor_meia'],
                    'valor_infantil': servico_data['valor_infantil'],
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Criado: {servico.nome} ({categoria.nome})'))
            else:
                self.stdout.write(self.style.WARNING(f'  - Já existe: {servico.nome}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Dados populados com sucesso!'))
        self.stdout.write(self.style.SUCCESS(f'  - {TipoMeiaEntrada.objects.count()} tipos de meia entrada'))
        self.stdout.write(self.style.SUCCESS(f'  - {Categoria.objects.count()} categorias'))
        self.stdout.write(self.style.SUCCESS(f'  - {SubCategoria.objects.count()} serviços'))
