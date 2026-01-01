"""
Comando para migrar dados de lançamentos do formato antigo para o novo
Converte:
- idades_criancas de string separada por vírgula para lista JSON
- tipos_meia_entrada de texto multilinha para ManyToManyField com TipoMeiaEntrada
"""
from django.core.management.base import BaseCommand
from servicos.models import LancamentoServico, TipoMeiaEntrada


class Command(BaseCommand):
    help = 'Migra dados de lançamentos para o novo formato'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando migração de dados...')
        
        # Contador
        migrados = 0
        erros = 0
        
        # Processar todos os lançamentos
        lancamentos = LancamentoServico.objects.all()
        total = lancamentos.count()
        
        self.stdout.write(f'Encontrados {total} lançamento(s) para processar')
        
        for lancamento in lancamentos:
            try:
                # Já está no formato novo (lista), pular
                if isinstance(lancamento.idades_criancas, list):
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Lançamento #{lancamento.id} já migrado')
                    )
                    continue
                
                # Converter idades de string para lista
                if lancamento.idades_criancas and isinstance(lancamento.idades_criancas, str):
                    idades_str = lancamento.idades_criancas.strip()
                    if idades_str:
                        # Separar por vírgula e converter para inteiros
                        idades = [int(idade.strip()) for idade in idades_str.split(',') if idade.strip()]
                        lancamento.idades_criancas = idades
                        lancamento.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Lançamento #{lancamento.id}: Idades migradas: {idades}'
                            )
                        )
                        migrados += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Lançamento #{lancamento.id}: Sem idades para migrar')
                    )
                    
            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Erro ao migrar lançamento #{lancamento.id}: {str(e)}')
                )
        
        # Resumo
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS(f'Total processado: {total}'))
        self.stdout.write(self.style.SUCCESS(f'Migrados com sucesso: {migrados}'))
        if erros > 0:
            self.stdout.write(self.style.ERROR(f'Erros: {erros}'))
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('Migração concluída!'))
