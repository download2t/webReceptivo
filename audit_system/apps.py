from django.apps import AppConfig


class AuditSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit_system'
    verbose_name = 'Sistema de Auditoria'
    
    def ready(self):
        """Conecta os signals quando a aplicação estiver pronta"""
        import audit_system.signals  # noqa
