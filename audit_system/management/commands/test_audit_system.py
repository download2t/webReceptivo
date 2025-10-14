"""
Comando para testar o sistema de auditoria
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from audit_system.signals import (
    log_custom_action, log_user_activation, 
    log_group_membership_change, log_password_change
)
from audit_system.models import AuditLog


class Command(BaseCommand):
    help = 'Testa o sistema de auditoria criando logs de exemplo'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Número de logs de teste a criar (padrão: 10)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa todos os logs antes de criar novos'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        # Limpar logs existentes se solicitado
        if clear:
            deleted_count = AuditLog.objects.all().delete()[0]
            self.stdout.write(f"Removidos {deleted_count} logs existentes")
        
        # Obter usuário de teste (primeiro usuário disponível)
        try:
            test_user = User.objects.first()
            if not test_user:
                self.stdout.write(
                    self.style.ERROR("Nenhum usuário encontrado. Crie um usuário primeiro.")
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Erro ao obter usuário: {e}")
            )
            return
        
        # Obter grupo de teste
        test_group = Group.objects.first()
        
        self.stdout.write(f"Criando {count} logs de teste...")
        
        created_count = 0
        
        # Criar diferentes tipos de logs de teste
        actions_to_test = [
            ('system_startup', 'Sistema iniciado para testes', None),
            ('user_view', 'Visualização de usuário', test_user),
            ('data_export', 'Exportação de dados de teste', None),
            ('settings_change', 'Configuração alterada para teste', None),
            ('user_profile_update', 'Perfil de usuário atualizado', test_user),
        ]
        
        for i in range(count):
            # Alternar entre diferentes tipos de ação
            action_name, description, obj = actions_to_test[i % len(actions_to_test)]
            
            try:
                log_custom_action(
                    action_name=f"{action_name}_{i+1}",
                    obj=obj,
                    user=test_user,
                    extra_data={
                        'test_iteration': i + 1,
                        'description': description,
                        'is_test': True,
                        'batch_id': f"test_batch_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
                    }
                )
                created_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erro ao criar log {i+1}: {e}")
                )
        
        # Criar alguns logs específicos se temos objetos disponíveis
        if test_user:
            try:
                # Log de ativação de usuário
                log_user_activation(test_user, True)
                created_count += 1
                
                # Log de mudança de senha
                log_password_change(test_user)
                created_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Erro ao criar logs específicos: {e}")
                )
        
        if test_group and test_user:
            try:
                # Log de mudança de grupo
                log_group_membership_change(test_user, test_group, True)
                created_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Erro ao criar log de grupo: {e}")
                )
        
        # Estatísticas finais
        total_logs = AuditLog.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Teste concluído! "
                f"Criados: {created_count} logs de teste. "
                f"Total de logs no sistema: {total_logs}"
            )
        )
        
        # Mostrar alguns logs recentes
        recent_logs = AuditLog.objects.order_by('-timestamp')[:5]
        
        self.stdout.write("\nLogs mais recentes:")
        for log in recent_logs:
            self.stdout.write(
                f"  [{log.timestamp.strftime('%H:%M:%S')}] "
                f"{log.get_action_display()} - {log.object_repr}"
            )
