"""
Comando Django para aplicar configurações SMTP do banco de dados
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from company_settings.models import SMTPSettings


class Command(BaseCommand):
    help = 'Aplica as configurações SMTP do banco de dados ao Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--show-current',
            action='store_true',
            help='Mostra as configurações atuais'
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Aplica as configurações do banco ao Django'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Testa o envio de e-mail com as configurações atuais'
        )

    def handle(self, *args, **options):
        if options['show_current']:
            self.show_current_settings()
        
        if options['apply']:
            self.apply_smtp_settings()
        
        if options['test']:
            self.test_email_sending()
        
        if not any([options['show_current'], options['apply'], options['test']]):
            self.stdout.write(
                self.style.WARNING(
                    'Use --show-current, --apply ou --test. Use --help para mais opções.'
                )
            )

    def show_current_settings(self):
        """Mostra as configurações SMTP atuais"""
        self.stdout.write(
            self.style.SUCCESS('📧 Configurações SMTP Atuais:')
        )
        
        try:
            smtp_settings = SMTPSettings.get_settings()
            
            self.stdout.write(f"Backend: {getattr(settings, 'EMAIL_BACKEND', 'Não definido')}")
            self.stdout.write(f"Host: {getattr(settings, 'EMAIL_HOST', 'Não definido')}")
            self.stdout.write(f"Porta: {getattr(settings, 'EMAIL_PORT', 'Não definido')}")
            self.stdout.write(f"Usuário: {getattr(settings, 'EMAIL_HOST_USER', 'Não definido')}")
            self.stdout.write(f"TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
            self.stdout.write(f"SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
            self.stdout.write(f"From padrão: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Não definido')}")
            
            self.stdout.write("\n📋 Configurações no Banco de Dados:")
            self.stdout.write(f"Ativo: {'✅' if smtp_settings.is_active else '❌'}")
            self.stdout.write(f"Backend: {smtp_settings.email_backend}")
            self.stdout.write(f"Servidor: {smtp_settings.smtp_server}")
            self.stdout.write(f"Porta: {smtp_settings.smtp_port}")
            self.stdout.write(f"Usuário: {smtp_settings.smtp_username}")
            self.stdout.write(f"Segurança: {smtp_settings.connection_security}")
            self.stdout.write(f"From: {smtp_settings.from_email}")
            self.stdout.write(f"Default From: {smtp_settings.default_from_email}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao carregar configurações: {e}')
            )

    def apply_smtp_settings(self):
        """Aplica as configurações SMTP do banco ao Django"""
        try:
            smtp_settings = SMTPSettings.get_settings()
            
            if not smtp_settings.is_active:
                self.stdout.write(
                    self.style.WARNING(
                        'As configurações SMTP não estão ativadas no banco de dados.'
                    )
                )
                return
            
            success = smtp_settings.apply_to_django_settings()
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Configurações SMTP aplicadas com sucesso!')
                )
                
                # Mostrar configurações aplicadas
                self.stdout.write("\n📧 Configurações Aplicadas:")
                self.stdout.write(f"Host: {settings.EMAIL_HOST}")
                self.stdout.write(f"Porta: {settings.EMAIL_PORT}")
                self.stdout.write(f"Usuário: {settings.EMAIL_HOST_USER}")
                self.stdout.write(f"TLS: {settings.EMAIL_USE_TLS}")
                self.stdout.write(f"SSL: {settings.EMAIL_USE_SSL}")
                self.stdout.write(f"From padrão: {settings.DEFAULT_FROM_EMAIL}")
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Erro ao aplicar configurações SMTP')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro: {e}')
            )

    def test_email_sending(self):
        """Testa o envio de e-mail"""
        try:
            from django.core.mail import send_mail
            
            # Aplicar configurações primeiro
            smtp_settings = SMTPSettings.get_settings()
            if smtp_settings.is_active:
                smtp_settings.apply_to_django_settings()
            
            # Obter e-mail de teste
            test_email = smtp_settings.default_from_email or smtp_settings.from_email
            
            if not test_email:
                self.stdout.write(
                    self.style.ERROR('Nenhum e-mail configurado para teste')
                )
                return
            
            self.stdout.write(f"🧪 Testando envio para: {test_email}")
            
            # Enviar e-mail de teste
            send_mail(
                subject='Teste de Configuração SMTP - WebReceptivo',
                message='Este é um e-mail de teste para verificar se as configurações SMTP estão funcionando corretamente.',
                from_email=test_email,
                recipient_list=[test_email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ E-mail de teste enviado com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro no teste de e-mail: {e}')
            )
