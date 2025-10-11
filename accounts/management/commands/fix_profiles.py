from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Verifica e corrige perfis de usuário existentes'

    def handle(self, *args, **options):
        users_without_profile = 0
        profiles_created = 0
        
        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                profiles_created += 1
                self.stdout.write(f'Perfil criado para usuário: {user.username}')
            else:
                self.stdout.write(f'Perfil já existe para usuário: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Verificação concluída! {profiles_created} perfis criados.')
        )
