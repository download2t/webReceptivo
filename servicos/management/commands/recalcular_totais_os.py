"""
Comando para recalcular os valores totais de todas as Ordens de Serviço
"""
from django.core.management.base import BaseCommand
from servicos.models import OrdemServico


class Command(BaseCommand):
    help = 'Recalcula os valores totais de todas as Ordens de Serviço'

    def handle(self, *args, **options):
        self.stdout.write('Recalculando valores totais das Ordens de Serviço...')
        
        ordens = OrdemServico.objects.all()
        total_ordens = ordens.count()
        
        self.stdout.write(f'Encontradas {total_ordens} Ordens de Serviço')
        
        for idx, ordem in enumerate(ordens, 1):
            valor_anterior = ordem.valor_total
            ordem.calcular_total()
            valor_novo = ordem.valor_total
            
            if valor_anterior != valor_novo:
                self.stdout.write(
                    self.style.WARNING(
                        f'[{idx}/{total_ordens}] OS #{ordem.numero_os}: '
                        f'R$ {valor_anterior} → R$ {valor_novo}'
                    )
                )
            else:
                self.stdout.write(
                    f'[{idx}/{total_ordens}] OS #{ordem.numero_os}: R$ {valor_novo} (sem alteração)'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Recálculo concluído! {total_ordens} Ordens de Serviço processadas.'
            )
        )
