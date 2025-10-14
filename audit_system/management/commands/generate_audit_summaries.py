"""
Comando para gerar resumos de auditoria periodicamente
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from audit_system.models import AuditLog, AuditLogSummary
from django.db.models import Count
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Gera resumos de auditoria para otimização de consultas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de dias para gerar resumos (padrão: 30)'
        )
        
        parser.add_argument(
            '--clean-old',
            action='store_true',
            help='Remove resumos antigos antes de gerar novos'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        clean_old = options['clean_old']
        
        self.stdout.write(f"Gerando resumos de auditoria para os últimos {days} dias...")
        
        # Limpar resumos antigos se solicitado
        if clean_old:
            deleted_count = AuditLogSummary.objects.all().delete()[0]
            self.stdout.write(f"Removidos {deleted_count} resumos antigos")
        
        # Calcular data de início
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Gerar resumos por data, usuário e ação
        logs_queryset = AuditLog.objects.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        )
        
        # Agrupar por data, usuário e ação
        summaries = (logs_queryset
                    .values('timestamp__date', 'user', 'action')
                    .annotate(count=Count('id'))
                    .order_by('timestamp__date', 'user', 'action'))
        
        created_count = 0
        updated_count = 0
        
        for summary_data in summaries:
            date = summary_data['timestamp__date']
            user_id = summary_data['user']
            action = summary_data['action']
            count = summary_data['count']
            
            # Obter usuário se existir
            user = None
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                except User.DoesNotExist:
                    pass
            
            # Criar ou atualizar resumo
            summary, created = AuditLogSummary.objects.get_or_create(
                date=date,
                user=user,
                action=action,
                defaults={'count': count}
            )
            
            if created:
                created_count += 1
            else:
                if summary.count != count:
                    summary.count = count
                    summary.save()
                    updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Resumos gerados com sucesso! "
                f"Criados: {created_count}, Atualizados: {updated_count}"
            )
        )
