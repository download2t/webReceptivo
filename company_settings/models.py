"""
Models para configurações da empresa
"""
from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone
from audit_system.models import AuditLog
from audit_system.signals import log_settings_change
import pytz
import json


class CompanySettings(models.Model):
    """Configurações gerais da empresa"""
    
    # Dados da Empresa
    company_name = models.CharField('Nome da Empresa', max_length=200)
    cnpj_cpf = models.CharField('CNPJ/CPF', max_length=20)
    state_registration = models.CharField('Inscrição Estadual', max_length=20, blank=True)
    
    # Endereço
    street = models.CharField('Logradouro', max_length=200)
    number = models.CharField('Número', max_length=10)
    complement = models.CharField('Complemento', max_length=100, blank=True)
    neighborhood = models.CharField('Bairro', max_length=100)
    city = models.CharField('Cidade', max_length=100)
    state = models.CharField('Estado', max_length=2, choices=[
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'),
        ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'),
        ('TO', 'Tocantins')
    ])
    zip_code = models.CharField('CEP', max_length=10)
    
    # Contato
    phone = models.CharField('Telefone Principal', max_length=20)
    email = models.EmailField('E-mail Principal')
    
    # Logotipo
    logo = models.ImageField('Logotipo', upload_to='company/logos/', blank=True, null=True)
    
    # Sistema
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Atualizado por')
    
    class Meta:
        verbose_name = 'Configurações da Empresa'
        verbose_name_plural = 'Configurações da Empresa'
    
    def __str__(self):
        return self.company_name
    
    @classmethod
    def get_settings(cls):
        """Retorna as configurações da empresa, criando uma instância se não existir"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'company_name': 'WebReceptivo',
                'cnpj_cpf': '00.000.000/0000-00',
                'street': 'Rua Principal',
                'number': '123',
                'neighborhood': 'Centro',
                'city': 'São Paulo',
                'state': 'SP',
                'zip_code': '00000-000',
                'phone': '(11) 0000-0000',
                'email': 'contato@webreceptivo.com'
            }
        )
        return settings
    
    def log_changes(self, user=None, request=None, changes_data=None):
        """Registra alterações nas configurações da empresa"""
        AuditLog.log_action(
            action='SETTINGS_CHANGED',
            obj=self,
            user=user,
            request=request,
            changes=changes_data or {},
            extra_data={
                'settings_type': 'company',
                'company_name': self.company_name
            }
        )


class SystemSettings(models.Model):
    """Configurações de sistema (data, hora, fuso)"""
    
    DATE_FORMAT_CHOICES = [
        ('d/m/Y', 'DD/MM/AAAA'),
        ('m/d/Y', 'MM/DD/AAAA'),
        ('Y-m-d', 'AAAA-MM-DD'),
        ('d-m-Y', 'DD-MM-AAAA'),
    ]
    
    TIME_FORMAT_CHOICES = [
        ('H:i', '24 horas (HH:MM)'),
        ('g:i A', '12 horas (H:MM AM/PM)'),
    ]
    
    # Formatação
    date_format = models.CharField(
        'Formato de Data', 
        max_length=10, 
        choices=DATE_FORMAT_CHOICES, 
        default='d/m/Y'
    )
    time_format = models.CharField(
        'Formato de Hora', 
        max_length=10, 
        choices=TIME_FORMAT_CHOICES, 
        default='H:i'
    )
    
    # Fuso Horário
    timezone = models.CharField(
        'Fuso Horário',
        max_length=50,
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default='America/Sao_Paulo'
    )
    
    # Sistema
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Atualizado por')
    
    class Meta:
        verbose_name = 'Configurações de Sistema'
        verbose_name_plural = 'Configurações de Sistema'
    
    def __str__(self):
        return f"Configurações - {self.timezone}"
    
    @classmethod
    def get_settings(cls):
        """Retorna as configurações de sistema, criando uma instância se não existir"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def get_current_datetime(self):
        """Retorna a data/hora atual no fuso configurado"""
        tz = pytz.timezone(self.timezone)
        return timezone.now().astimezone(tz)
    
    def log_changes(self, user=None, request=None, changes_data=None):
        """Registra alterações nas configurações de sistema"""
        AuditLog.log_action(
            action='SETTINGS_CHANGED',
            obj=self,
            user=user,
            request=request,
            changes=changes_data or {},
            extra_data={
                'settings_type': 'system',
                'timezone': self.timezone,
                'date_format': self.date_format,
                'time_format': self.time_format
            }
        )


class SMTPSettings(models.Model):
    """Configurações de SMTP para envio de e-mails"""
    
    CONNECTION_CHOICES = [
        ('ssl', 'SSL'),
        ('tls', 'TLS'),
        ('starttls', 'STARTTLS'),
        ('none', 'Sem criptografia'),
    ]
    
    BACKEND_CHOICES = [
        ('django.core.mail.backends.smtp.EmailBackend', 'SMTP Backend (Padrão)'),
        ('django.core.mail.backends.console.EmailBackend', 'Console Backend (Desenvolvimento)'),
        ('django.core.mail.backends.filebased.EmailBackend', 'File Backend (Arquivo)'),
        ('django.core.mail.backends.locmem.EmailBackend', 'Memory Backend (Memória)'),
        ('django.core.mail.backends.dummy.EmailBackend', 'Dummy Backend (Teste)'),
    ]
    
    # Backend
    email_backend = models.CharField(
        'Backend de E-mail', 
        max_length=255, 
        choices=BACKEND_CHOICES,
        default='django.core.mail.backends.smtp.EmailBackend'
    )
    
    # Servidor
    smtp_server = models.CharField('Servidor SMTP', max_length=255)
    smtp_port = models.PositiveIntegerField('Porta', default=587)
    connection_security = models.CharField(
        'Tipo de Conexão', 
        max_length=10, 
        choices=CONNECTION_CHOICES, 
        default='tls'
    )
    
    # E-mail único (usado para autenticação, remetente e padrão do sistema)
    email = models.EmailField('E-mail SMTP', default='noreply@webreceptivo.com', help_text='E-mail usado para autenticação, remetente e todas as funções do sistema')
    smtp_password = models.CharField('Senha SMTP', max_length=255)
    
    # Configurações extras
    use_authentication = models.BooleanField('Usar Autenticação', default=True)
    timeout = models.PositiveIntegerField('Timeout (segundos)', default=30)
    
    # Ativação das configurações
    is_active = models.BooleanField('Ativar Configurações', default=True, help_text='Se ativado, o sistema usará estas configurações para envio de e-mails')
    
    # Teste de conexão
    last_test_date = models.DateTimeField('Último Teste', null=True, blank=True)
    last_test_success = models.BooleanField('Último Teste Sucesso', default=False)
    last_test_message = models.TextField('Mensagem do Último Teste', blank=True)
    
    # Sistema
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Atualizado por')
    
    class Meta:
        verbose_name = 'Configurações de SMTP'
        verbose_name_plural = 'Configurações de SMTP'
    
    def __str__(self):
        return f"{self.smtp_server}:{self.smtp_port}"
    
    @classmethod
    def get_settings(cls):
        """Retorna as configurações de SMTP, criando uma instância se não existir"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'connection_security': 'tls',
                'email': 'noreply@webreceptivo.com',
                'smtp_password': '',
            }
        )
        return settings
    
    def test_connection(self, test_email=None):
        """Testa a conexão SMTP
        
        Args:
            test_email (str, optional): E-mail de destino para o teste. 
                                      Se não fornecido, usa o email configurado.
        """
        try:
            from django.core.mail import send_mail
            from django.conf import settings as django_settings
            
            # Definir e-mail de destino
            recipient_email = test_email if test_email else self.email
            
            # Configurar temporariamente as configurações de e-mail
            original_settings = {}
            email_settings = {
                'EMAIL_HOST': self.smtp_server,
                'EMAIL_PORT': self.smtp_port,
                'EMAIL_HOST_USER': self.email,
                'EMAIL_HOST_PASSWORD': self.smtp_password,
                'EMAIL_USE_TLS': self.connection_security in ['tls', 'starttls'],
                'EMAIL_USE_SSL': self.connection_security == 'ssl',
                'DEFAULT_FROM_EMAIL': self.email,
            }
            
            # Salvar configurações originais
            for key in email_settings:
                if hasattr(django_settings, key):
                    original_settings[key] = getattr(django_settings, key)
                setattr(django_settings, key, email_settings[key])
            
            try:
                # Tentar enviar e-mail de teste
                send_mail(
                    subject='Teste de Conexão SMTP - WebReceptivo',
                    message=f'Este é um e-mail de teste para verificar a configuração SMTP.\n\nEnviado de: {self.email}\nPara: {recipient_email}\n\nSe você recebeu este e-mail, a configuração SMTP está funcionando corretamente!',
                    from_email=self.email,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                
                self.last_test_success = True
                self.last_test_message = f'E-mail de teste enviado com sucesso para {recipient_email}!'
                
            except Exception as e:
                self.last_test_success = False
                self.last_test_message = f'Erro na conexão SMTP: {str(e)}'
            
            finally:
                # Restaurar configurações originais
                for key, value in original_settings.items():
                    setattr(django_settings, key, value)
            
            self.last_test_date = timezone.now()
            self.save()
            
            return self.last_test_success, self.last_test_message
            
        except Exception as e:
            self.last_test_success = False
            self.last_test_message = f'Erro interno: {str(e)}'
            self.last_test_date = timezone.now()
            self.save()
            return False, self.last_test_message
    
    def apply_to_django_settings(self):
        """Aplica as configurações SMTP ao Django dinamicamente"""
        from django.conf import settings
        
        if not self.is_active:
            return False
        
        # Aplicar configurações de e-mail ao Django
        settings.EMAIL_BACKEND = self.email_backend
        settings.EMAIL_HOST = self.smtp_server
        settings.EMAIL_PORT = self.smtp_port
        settings.EMAIL_HOST_USER = self.email
        settings.EMAIL_HOST_PASSWORD = self.smtp_password
        
        # Configurar TLS/SSL
        if self.connection_security == 'tls':
            settings.EMAIL_USE_TLS = True
            settings.EMAIL_USE_SSL = False
        elif self.connection_security == 'ssl':
            settings.EMAIL_USE_TLS = False
            settings.EMAIL_USE_SSL = True
        else:
            settings.EMAIL_USE_TLS = False
            settings.EMAIL_USE_SSL = False
        
        # Configurar e-mail padrão (usar o mesmo e-mail único)
        settings.DEFAULT_FROM_EMAIL = self.email
        
        # Configurar timeout se suportado
        if hasattr(settings, 'EMAIL_TIMEOUT'):
            settings.EMAIL_TIMEOUT = self.timeout
        
        return True
    
    @classmethod
    def load_and_apply_settings(cls):
        """Carrega e aplica as configurações SMTP ativas"""
        try:
            smtp_settings = cls.get_settings()
            if smtp_settings.is_active:
                return smtp_settings.apply_to_django_settings()
            return False
        except Exception:
            return False
    
    def get_django_settings_dict(self):
        """Retorna as configurações como dicionário para uso direto"""
        settings_dict = {
            'EMAIL_BACKEND': self.email_backend,
            'EMAIL_HOST': self.smtp_server,
            'EMAIL_PORT': self.smtp_port,
            'EMAIL_HOST_USER': self.smtp_username,
            'EMAIL_HOST_PASSWORD': self.smtp_password,
            'EMAIL_USE_TLS': self.connection_security == 'tls',
            'EMAIL_USE_SSL': self.connection_security == 'ssl',
            'DEFAULT_FROM_EMAIL': self.email,
        }
        
        if self.timeout:
            settings_dict['EMAIL_TIMEOUT'] = self.timeout
            
        return settings_dict
    
    def log_changes(self, user=None, request=None, changes_data=None):
        """Registra alterações nas configurações de SMTP"""
        # Não registrar senha nas mudanças por segurança
        safe_changes = changes_data.copy() if changes_data else {}
        if 'smtp_password' in safe_changes:
            safe_changes['smtp_password'] = '***PASSWORD_CHANGED***'
        
        AuditLog.log_action(
            action='SETTINGS_CHANGED',
            obj=self,
            user=user,
            request=request,
            changes=safe_changes,
            extra_data={
                'settings_type': 'smtp',
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port,
                'email': self.email
            }
        )
    
    def log_test_connection(self, user=None, request=None, success=False, message=''):
        """Registra teste de conexão SMTP"""
        AuditLog.log_action(
            action='CUSTOM_ACTION',
            obj=self,
            user=user,
            request=request,
            success=success,
            error_message=message if not success else None,
            extra_data={
                'custom_action_name': 'smtp_test_connection',
                'test_result': 'success' if success else 'failed',
                'test_message': message,
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port
            }
        )
