from django.contrib.auth.models import User

# Verificar se já existe um superusuário
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@webreceptivo.com', 'admin123')
    print("Superusuário 'admin' criado com sucesso!")
else:
    print("Superusuário 'admin' já existe.")
