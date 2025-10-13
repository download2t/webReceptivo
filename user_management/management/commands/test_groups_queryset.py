"""
Comando para testar especificamente o queryset de grupos e identificar o erro de union.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user_management.permission_helpers import get_manageable_groups_queryset, get_user_level


class Command(BaseCommand):
    help = 'Testa o queryset de grupos para diferentes níveis de usuário'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID do usuário para testar (padrão: testa todos os tipos)',
        )
    
    def handle(self, *args, **options):
        user_id = options.get('user_id')
        
        if user_id:
            # Testar usuário específico
            try:
                user = User.objects.get(id=user_id)
                self.test_user_groups_queryset(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Usuário com ID {user_id} não encontrado')
                )
        else:
            # Testar todos os tipos de usuário
            self.test_all_user_types()
    
    def test_user_groups_queryset(self, user):
        """Testa o queryset de grupos para um usuário específico"""
        self.stdout.write(f"\n=== TESTANDO USUÁRIO: {user.username} (ID: {user.id}) ===")
        
        # Obter nível do usuário
        user_level = get_user_level(user)
        self.stdout.write(f"Nível do usuário: {user_level}")
        
        try:
            # Testar get_manageable_groups_queryset
            self.stdout.write("1. Testando get_manageable_groups_queryset()...")
            queryset = get_manageable_groups_queryset(user)
            self.stdout.write(f"   ✓ Queryset obtido: {queryset}")
            
            # Testar count()
            self.stdout.write("2. Testando .count()...")
            count = queryset.count()
            self.stdout.write(f"   ✓ Count: {count}")
            
            # Testar prefetch_related
            self.stdout.write("3. Testando .prefetch_related('permissions')...")
            prefetched_queryset = queryset.prefetch_related('permissions')
            self.stdout.write(f"   ✓ Prefetch aplicado: {prefetched_queryset}")
            
            # Testar list() (força execução da query)
            self.stdout.write("4. Testando execução da query (list)...")
            groups = list(prefetched_queryset)
            self.stdout.write(f"   ✓ Query executada: {len(groups)} grupos encontrados")
            
            # Listar grupos
            for group in groups:
                self.stdout.write(f"     - {group.name} ({group.permissions.count()} permissões)")
                
            self.stdout.write(
                self.style.SUCCESS(f"✓ SUCESSO para usuário {user.username}")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ ERRO para usuário {user.username}: {e}")
            )
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def test_all_user_types(self):
        """Testa para todos os tipos de usuário disponíveis"""
        self.stdout.write("=== TESTANDO TODOS OS TIPOS DE USUÁRIO ===\n")
        
        # Obter usuários de cada tipo
        users_to_test = []
        
        # Admin principal (ID=1)
        try:
            admin_principal = User.objects.get(id=1)
            users_to_test.append(admin_principal)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("Admin principal (ID=1) não encontrado")
            )
        
        # Administrador
        try:
            admin = User.objects.filter(groups__name='Administradores').first()
            if admin:
                users_to_test.append(admin)
        except:
            pass
        
        # Gerente
        try:
            gerente = User.objects.filter(groups__name='Gerentes').first()
            if gerente:
                users_to_test.append(gerente)
        except:
            pass
        
        # Operador
        try:
            operador = User.objects.filter(groups__name='Operadores').first()
            if operador:
                users_to_test.append(operador)
        except:
            pass
        
        # Usuário básico
        try:
            usuario = User.objects.filter(groups__name='Usuários Básicos').first()
            if usuario:
                users_to_test.append(usuario)
        except:
            pass
        
        # Testar cada usuário
        for user in users_to_test:
            self.test_user_groups_queryset(user)
        
        self.stdout.write(f"\n=== TESTE CONCLUÍDO ===")
