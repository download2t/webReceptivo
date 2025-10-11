from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser for WebReceptivo'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@webreceptivo.com', 
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('Superusuário "admin" criado com sucesso!')
            )
            self.stdout.write('Username: admin')
            self.stdout.write('Password: admin123')
        else:
            self.stdout.write(
                self.style.WARNING('Superusuário "admin" já existe.')
            )
