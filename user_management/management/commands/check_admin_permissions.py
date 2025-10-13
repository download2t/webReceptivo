"""
Comando para verificar e ajustar permissões de acesso ao admin Django.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from user_management.permission_helpers import get_user_level, get_user_level_display


class Command(BaseCommand):
    help = 'Verifica e ajusta permissões de acesso ao admin Django'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corrige automaticamente as permissões de acesso ao admin',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("=== DIAGNÓSTICO DO ADMIN DJANGO ===\n")
        
        # 1. Verificar usuários
        self.check_users()
        
        # 2. Verificar grupos
        self.check_groups()
        
        # 3. Verificar permissões
        self.check_permissions()
        
        # 4. Corrigir se solicitado
        if options['fix']:
            self.fix_admin_permissions()
        
        self.stdout.write(f"\n=== DIAGNÓSTICO CONCLUÍDO ===")
    
    def check_users(self):
        """Verifica status dos usuários para acesso ao admin"""
        self.stdout.write("📊 VERIFICANDO USUÁRIOS:")
        
        users = User.objects.all().order_by('id')
        
        for user in users:
            level = get_user_level(user)
            level_display = get_user_level_display(user)
            
            status_indicators = []
            if user.is_active:
                status_indicators.append("✅ Ativo")
            else:
                status_indicators.append("❌ Inativo")
                
            if user.is_staff:
                status_indicators.append("🔧 Staff")
            else:
                status_indicators.append("👤 Usuário")
                
            if user.is_superuser:
                status_indicators.append("⭐ Superuser")
            
            groups = list(user.groups.values_list('name', flat=True))
            groups_str = ", ".join(groups) if groups else "Nenhum"
            
            self.stdout.write(f"  👤 {user.username} (ID: {user.id})")
            self.stdout.write(f"     Nível: {level_display}")
            self.stdout.write(f"     Status: {' | '.join(status_indicators)}")
            self.stdout.write(f"     Grupos: {groups_str}")
            self.stdout.write(f"     Email: {user.email or 'Não informado'}")
            
            # Verificar se deveria ter acesso ao admin
            should_have_admin = level in ['admin_principal', 'administrador', 'gerente']
            has_admin = user.is_staff
            
            if should_have_admin and not has_admin:
                self.stdout.write(f"     ⚠️  PROBLEMA: Deveria ter acesso ao admin mas não tem is_staff=True")
            elif not should_have_admin and has_admin:
                self.stdout.write(f"     ⚠️  ATENÇÃO: Tem acesso ao admin mas nível não requer")
            else:
                self.stdout.write(f"     ✅ Permissões de admin corretas")
            
            self.stdout.write("")
    
    def check_groups(self):
        """Verifica grupos disponíveis"""
        self.stdout.write("📋 VERIFICANDO GRUPOS:")
        
        groups = Group.objects.all().order_by('name')
        
        for group in groups:
            user_count = group.user_set.count()
            perm_count = group.permissions.count()
            
            self.stdout.write(f"  📁 {group.name}")
            self.stdout.write(f"     Usuários: {user_count}")
            self.stdout.write(f"     Permissões: {perm_count}")
            
            if user_count > 0:
                users_in_group = list(group.user_set.values_list('username', flat=True))
                self.stdout.write(f"     Membros: {', '.join(users_in_group)}")
            
            self.stdout.write("")
    
    def check_permissions(self):
        """Verifica permissões críticas"""
        self.stdout.write("🔑 VERIFICANDO PERMISSÕES CRÍTICAS:")
        
        # Permissões importantes para o admin
        critical_perms = [
            'auth.add_user',
            'auth.change_user', 
            'auth.delete_user',
            'auth.view_user',
            'auth.add_group',
            'auth.change_group',
            'auth.delete_group',
            'auth.view_group',
        ]
        
        for perm_name in critical_perms:
            try:
                app_label, codename = perm_name.split('.')
                perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                
                # Usuários com essa permissão diretamente
                users_with_perm = User.objects.filter(user_permissions=perm).count()
                
                # Grupos com essa permissão
                groups_with_perm = Group.objects.filter(permissions=perm)
                groups_count = groups_with_perm.count()
                
                self.stdout.write(f"  🔑 {perm_name}")
                self.stdout.write(f"     Usuários diretos: {users_with_perm}")
                self.stdout.write(f"     Grupos: {groups_count}")
                
                if groups_count > 0:
                    group_names = list(groups_with_perm.values_list('name', flat=True))
                    self.stdout.write(f"     Grupos com permissão: {', '.join(group_names)}")
                
                self.stdout.write("")
                
            except Permission.DoesNotExist:
                self.stdout.write(f"  ❌ Permissão {perm_name} não encontrada!")
                self.stdout.write("")
    
    def fix_admin_permissions(self):
        """Corrige permissões de acesso ao admin"""
        self.stdout.write("🔧 CORRIGINDO PERMISSÕES:")
        
        users = User.objects.all()
        fixed_count = 0
        
        for user in users:
            level = get_user_level(user)
            # Administradores e gerentes devem ter acesso ao admin
            should_be_staff = level in ['admin_principal', 'administrador', 'gerente']
            
            if should_be_staff and not user.is_staff:
                user.is_staff = True
                user.save()
                self.stdout.write(f"  ✅ Adicionado is_staff=True para {user.username}")
                fixed_count += 1
            
            # Admin principal deve ser superuser
            if level == 'admin_principal' and not user.is_superuser:
                user.is_superuser = True
                user.save()
                self.stdout.write(f"  ✅ Adicionado is_superuser=True para {user.username}")
                fixed_count += 1
        
        # Adicionar permissões básicas aos grupos
        self.add_basic_permissions_to_groups()
        
        if fixed_count > 0:
            self.stdout.write(f"\n🎉 {fixed_count} correções aplicadas!")
        else:
            self.stdout.write(f"\n✅ Nenhuma correção necessária!")
    
    def add_basic_permissions_to_groups(self):
        """Adiciona permissões básicas aos grupos para acesso ao admin"""
        
        # Permissões para Administradores
        try:
            admin_group = Group.objects.get(name='Administradores')
            admin_perms = Permission.objects.filter(
                content_type__app_label='auth',
                codename__in=['add_user', 'change_user', 'delete_user', 'view_user', 
                             'add_group', 'change_group', 'view_group']
            )
            
            added_count = 0
            for perm in admin_perms:
                if not admin_group.permissions.filter(pk=perm.pk).exists():
                    admin_group.permissions.add(perm)
                    added_count += 1
            
            if added_count > 0:
                self.stdout.write(f"  ✅ Adicionadas {added_count} permissões ao grupo Administradores")
        
        except Group.DoesNotExist:
            self.stdout.write(f"  ⚠️  Grupo Administradores não encontrado")
        
        # Permissões para Gerentes
        try:
            manager_group = Group.objects.get(name='Gerentes')
            manager_perms = Permission.objects.filter(
                content_type__app_label='auth',
                codename__in=['view_user', 'view_group']
            )
            
            added_count = 0
            for perm in manager_perms:
                if not manager_group.permissions.filter(pk=perm.pk).exists():
                    manager_group.permissions.add(perm)
                    added_count += 1
            
            if added_count > 0:
                self.stdout.write(f"  ✅ Adicionadas {added_count} permissões ao grupo Gerentes")
        
        except Group.DoesNotExist:
            self.stdout.write(f"  ⚠️  Grupo Gerentes não encontrado")
