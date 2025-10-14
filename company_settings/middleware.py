"""
Middleware para aplicar configurações SMTP dinâmicas do banco de dados
"""
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ImproperlyConfigured


class DynamicSMTPMiddleware(MiddlewareMixin):
    """
    Middleware para aplicar configurações SMTP do banco de dados dinamicamente
    """
    
    _smtp_applied = False
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        
    def process_request(self, request):
        """
        Aplica configurações SMTP na primeira requisição se não foram aplicadas ainda
        """
        if not self._smtp_applied:
            try:
                self.apply_smtp_settings()
                DynamicSMTPMiddleware._smtp_applied = True
            except Exception:
                # Se falhar, continua com as configurações padrão do settings.py
                pass
        
        return None
    
    def apply_smtp_settings(self):
        """
        Aplica as configurações SMTP do banco de dados ao Django
        """
        try:
            from company_settings.models import SMTPSettings
            
            # Tentar carregar e aplicar as configurações
            result = SMTPSettings.load_and_apply_settings()
            
            if result:
                print("✅ Configurações SMTP dinâmicas aplicadas com sucesso!")
            else:
                print("ℹ️ Usando configurações SMTP padrão do settings.py")
                
        except Exception as e:
            print(f"⚠️ Erro ao aplicar configurações SMTP dinâmicas: {e}")
            # Em caso de erro, usa as configurações padrão do settings.py


class SMTPConfigManager:
    """
    Gerenciador de configurações SMTP para uso em views e outros locais
    """
    
    @staticmethod
    def get_current_settings():
        """
        Retorna as configurações SMTP atuais (do banco ou padrão)
        """
        try:
            from company_settings.models import SMTPSettings
            smtp_settings = SMTPSettings.get_settings()
            
            if smtp_settings.is_active:
                return smtp_settings.get_django_settings_dict()
            else:
                return SMTPConfigManager.get_default_settings()
                
        except Exception:
            return SMTPConfigManager.get_default_settings()
    
    @staticmethod
    def get_default_settings():
        """
        Retorna as configurações padrão do settings.py
        """
        from django.conf import settings
        
        return {
            'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'),
            'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'localhost'),
            'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 25),
            'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', ''),
            'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
            'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', False),
            'EMAIL_USE_SSL': getattr(settings, 'EMAIL_USE_SSL', False),
            'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost'),
        }
    
    @staticmethod
    def apply_settings_temporarily(smtp_settings_dict):
        """
        Aplica configurações temporariamente para uma operação específica
        """
        from django.conf import settings
        
        # Salvar configurações originais
        original_settings = {}
        for key in smtp_settings_dict.keys():
            if hasattr(settings, key):
                original_settings[key] = getattr(settings, key)
        
        # Aplicar novas configurações
        for key, value in smtp_settings_dict.items():
            setattr(settings, key, value)
        
        return original_settings
    
    @staticmethod
    def restore_settings(original_settings):
        """
        Restaura configurações originais
        """
        from django.conf import settings
        
        for key, value in original_settings.items():
            setattr(settings, key, value)


def send_email_with_dynamic_config(subject, message, from_email=None, recipient_list=None, **kwargs):
    """
    Função helper para enviar e-mail usando configurações dinâmicas
    """
    from django.core.mail import send_mail
    
    # Obter configurações atuais
    current_config = SMTPConfigManager.get_current_settings()
    
    # Aplicar configurações temporariamente
    original_settings = SMTPConfigManager.apply_settings_temporarily(current_config)
    
    try:
        # Usar e-mail padrão se não especificado
        if not from_email:
            from_email = current_config.get('DEFAULT_FROM_EMAIL')
        
        # Enviar e-mail
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list or [],
            **kwargs
        )
        
        return result
        
    finally:
        # Restaurar configurações originais
        SMTPConfigManager.restore_settings(original_settings)
