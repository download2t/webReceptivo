from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from datetime import date


class Command(BaseCommand):
    help = 'Testa a funcionalidade de data de nascimento'

    def handle(self, *args, **options):
        try:
            # Pegar o usuário admin
            user = User.objects.get(username='admin')
            profile = user.profile
            
            # Definir uma data de teste
            test_date = date(1990, 5, 15)
            profile.data_nascimento = test_date
            profile.save()
            
            # Verificar se foi salva
            profile.refresh_from_db()
            
            if profile.data_nascimento == test_date:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Data de nascimento salva corretamente: {profile.data_nascimento}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao salvar data de nascimento. Esperado: {test_date}, Atual: {profile.data_nascimento}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro durante o teste: {str(e)}')
            )
