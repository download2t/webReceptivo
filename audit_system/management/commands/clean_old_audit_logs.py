"""
Comando para limpar logs de auditoria antigos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from audit_system.models import AuditLog


class Command(BaseCommand):
    help = 'Remove logs de auditoria antigos para manter o banco de dados otimizado'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Logs mais antigos que X dias serão removidos (padrão: 365)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra quantos logs seriam removidos sem remover de fato'
        )
        
        parser.add_argument(
            '--keep-errors',
            action='store_true',
            help='Mantém logs de erro, mesmo que sejam antigos'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        keep_errors = options['keep_errors']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"Processando logs anteriores a {cutoff_date.date()}...")
        
        # Query base para logs antigos
        old_logs = AuditLog.objects.filter(timestamp__lt=cutoff_date)
        
        # Se manter erros, excluí-los da remoção
        if keep_errors:
            old_logs = old_logs.filter(success=True)
            self.stdout.write("Mantendo logs de erro (success=False)")
        
        total_count = old_logs.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS("Nenhum log antigo encontrado para remoção")
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: {total_count} logs seriam removidos"
                )
            )
            
            # Mostrar estatísticas por ação
            actions_stats = (old_logs
                           .values('action')
                           .annotate(count=Count('id'))
                           .order_by('-count'))
            
            self.stdout.write("\nEstatísticas por ação:")
            for stat in actions_stats[:10]:  # Top 10
                self.stdout.write(f"  {stat['action']}: {stat['count']} logs")
        
        else:
            # Confirmar ação
            if not self._confirm_deletion(total_count):
                self.stdout.write("Operação cancelada")
                return
            
            # Remover em lotes para evitar problemas de memória
            batch_size = 1000
            removed_count = 0
            
            while True:
                batch = list(old_logs[:batch_size])
                if not batch:
                    break
                
                batch_ids = [log.id for log in batch]
                deleted = AuditLog.objects.filter(id__in=batch_ids).delete()
                removed_count += deleted[0]
                
                self.stdout.write(f"Removidos {removed_count}/{total_count} logs...")
            
            self.stdout.write(
                self.style.SUCCESS(f"Limpeza concluída! {removed_count} logs removidos")
            )
    
    def _confirm_deletion(self, count):
        """Pede confirmação antes de deletar"""
        self.stdout.write(
            self.style.WARNING(f"ATENÇÃO: {count} logs serão removidos permanentemente!")
        )
        
        response = input("Deseja continuar? (digite 'confirmar' para prosseguir): ")
        return response.lower() == 'confirmar'
