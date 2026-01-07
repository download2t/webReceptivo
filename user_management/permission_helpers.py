"""
Helpers para validação de permissões e regras de negócio do sistema de usuários.

HIERARQUIA E REGRAS DE NEGÓCIO:

1. USUÁRIOS BÁSICOS:
   - Acesso apenas ao próprio perfil
   - Não acessam áreas administrativas
   - Podem alterar apenas seus próprios dados básicos

2. OPERADORES:
   - Acesso ao sistema operacional
   - Não acessam área de administração de usuários
   - Focados em operações do negócio

3. GERENTES:
   - Cadastram e alteram Operadores e Usuários Básicos
   - NÃO podem mexer em Administradores ou outros Gerentes
   - Acessam relatórios gerenciais
   - Podem visualizar usuários de nível inferior

4. ADMINISTRADORES:
   - Fazem tudo com Usuários, Operadores e Gerentes
   - NÃO podem alterar outros Administradores
   - NÃO podem mexer no Admin Principal (ID=1)
   - Acessam todas as áreas administrativas

5. ADMINISTRADOR PRINCIPAL (ID=1):
   - PROTEGIDO: Não pode ser editado, deletado ou ter privilégios removidos
   - Pode fazer qualquer coisa no sistema
   - Único que pode alterar outros Administradores
   - Sempre mantém is_superuser=True e is_active=True

REGRAS DE PROTEÇÃO:
- Ninguém pode editar a si mesmo através da administração
- Admin Principal (ID=1) é intocável por outros usuários
- Cada nível só pode gerenciar níveis inferiores
- Usuários não podem elevar privilégios além do que têm
"""

from django.contrib.auth.models import User, Group


def get_user_level(user):
    """
    Determina o nível hierárquico do usuário baseado nos grupos.
    Retorna: 'admin_principal', 'administrador', 'gerente', 'operador', 'usuario_basico'
    """
    if not user or not user.is_authenticated:
        return 'usuario_basico'
    
    # Admin principal (ID=1) sempre tem o maior nível
    if user.id == 1 and user.is_superuser:
        return 'admin_principal'
    
    # Verificar por grupos (em ordem de prioridade)
    user_groups = user.groups.values_list('name', flat=True)
    
    if 'Administradores' in user_groups or user.is_superuser:
        return 'administrador'
    elif 'Gerentes' in user_groups:
        return 'gerente'
    elif 'Operadores' in user_groups:
        return 'operador'
    else:
        return 'usuario_basico'


def can_access_user_management(user):
    """
    Verifica se o usuário pode acessar a área de gerenciamento de usuários.
    Apenas Gerentes e Administradores podem acessar.
    """
    user_level = get_user_level(user)
    return user_level in ['admin_principal', 'administrador', 'gerente']


def can_view_user(current_user, target_user):
    """
    Verifica se o usuário atual pode visualizar outro usuário na administração.
    
    Regras de visualização:
    - Admin Principal: vê todos
    - Administradores: vê gerentes, operadores e usuários (mas não admin principal ou outros admins)
    - Gerentes: vê apenas operadores e usuários básicos
    - Outros: não veem ninguém na administração
    """
    current_level = get_user_level(current_user)
    target_level = get_user_level(target_user)
    
    # Admin principal pode ver todos
    if current_level == 'admin_principal':
        return True
    
    # Administradores podem ver gerentes, operadores e usuários (mas não admin principal ou outros admins)
    if current_level == 'administrador':
        return target_level in ['gerente', 'operador', 'usuario_basico']
    
    # Gerentes podem ver apenas operadores e usuários básicos
    if current_level == 'gerente':
        return target_level in ['operador', 'usuario_basico']
    
    # Outros níveis não podem ver usuários na administração
    return False


def can_edit_user(current_user, target_user):
    """
    Verifica se o usuário atual pode editar outro usuário.
    
    Regras:
    - Ninguém edita a si mesmo via administração
    - Admin Principal (ID=1) é intocável
    - Cada nível gerencia apenas níveis inferiores
    """
    current_level = get_user_level(current_user)
    target_level = get_user_level(target_user)
    
    # Não pode editar a si mesmo através da administração
    if current_user.id == target_user.id:
        return False
    
    # Admin principal (ID=1) nunca pode ser editado por ninguém
    if target_user.id == 1:
        return False
    
    # Admin principal pode editar todos (exceto ID=1 já verificado acima)
    if current_level == 'admin_principal':
        return True
    
    # Administradores podem editar apenas gerentes, operadores e usuários básicos
    if current_level == 'administrador':
        return target_level in ['gerente', 'operador', 'usuario_basico']
    
    # Gerentes podem editar apenas operadores e usuários básicos
    if current_level == 'gerente':
        return target_level in ['operador', 'usuario_basico']
    
    # Outros níveis não podem editar ninguém
    return False


# FUNCIONALIDADE DE EXCLUSÃO DESATIVADA POR SEGURANÇA
# Apenas inativação de usuários é permitida para manter integridade dos dados
#
# def can_delete_user(current_user, target_user):
#     """
#     Verifica se o usuário atual pode deletar outro usuário.
#     DESATIVADA - Use inativação em vez de exclusão.
#     """
#     # Funcionalidade removida por segurança
#     return False


def can_create_user_with_level(current_user, target_level):
    """
    Verifica se o usuário atual pode criar um usuário com determinado nível.
    """
    current_level = get_user_level(current_user)
    
    # Admin principal pode criar qualquer nível
    if current_level == 'admin_principal':
        return True
    
    # Administradores podem criar até gerentes
    if current_level == 'administrador':
        return target_level in ['gerente', 'operador', 'usuario_basico']
    
    # Gerentes podem criar apenas operadores e usuários básicos
    if current_level == 'gerente':
        return target_level in ['operador', 'usuario_basico']
    
    # Outros não podem criar usuários
    return False


def can_change_user_groups(current_user, target_user, new_groups):
    """
    Verifica se o usuário atual pode alterar os grupos do usuário alvo.
    """
    # Se target_user é None (criação de novo usuário), permitir se pode criar com esse nível
    if target_user is None:
        # Para novo usuário, determinar o nível mais alto dos novos grupos
        highest_new_level = 'usuario_basico'
        for group in new_groups:
            if group.name == 'Administradores':
                highest_new_level = 'administrador'
                break
            elif group.name == 'Gerentes' and highest_new_level not in ['administrador']:
                highest_new_level = 'gerente'
            elif group.name == 'Operadores' and highest_new_level not in ['administrador', 'gerente']:
                highest_new_level = 'operador'
        return can_create_user_with_level(current_user, highest_new_level)
    
    current_level = get_user_level(current_user)
    target_level = get_user_level(target_user)
    
    # Admin principal (ID=1) não pode ter grupos alterados
    if target_user.id == 1:
        return False
    
    # Determinar o nível mais alto dos novos grupos
    highest_new_level = 'usuario_basico'
    for group in new_groups:
        if group.name == 'Administradores':
            highest_new_level = 'administrador'
            break
        elif group.name == 'Gerentes' and highest_new_level not in ['administrador']:
            highest_new_level = 'gerente'
        elif group.name == 'Operadores' and highest_new_level not in ['administrador', 'gerente']:
            highest_new_level = 'operador'
    
    # Verificar se pode criar usuário com esse nível
    return can_create_user_with_level(current_user, highest_new_level)


def can_toggle_active_status(current_user, target_user):
    """
    Verifica se pode ativar/inativar um usuário.
    """
    # Admin principal (ID=1) não pode ser inativado
    if target_user.id == 1:
        return False
    
    # Usar as mesmas regras de edição
    return can_edit_user(current_user, target_user)


def can_change_password(current_user, target_user):
    """
    Verifica se pode alterar a senha de um usuário.
    """
    # Usar as mesmas regras de edição
    return can_edit_user(current_user, target_user)


def get_allowed_groups_for_user(current_user):
    """
    Retorna os grupos que o usuário atual pode atribuir a outros usuários.
    """
    current_level = get_user_level(current_user)
    allowed_groups = []
    
    try:
        if current_level == 'admin_principal':
            # Admin principal pode atribuir qualquer grupo
            allowed_groups = Group.objects.all()
        elif current_level == 'administrador':
            # Administradores podem atribuir até gerentes
            allowed_groups = Group.objects.filter(
                name__in=['Gerentes', 'Operadores', 'Usuários Básicos']
            )
        elif current_level == 'gerente':
            # Gerentes podem atribuir apenas operadores e usuários básicos
            allowed_groups = Group.objects.filter(
                name__in=['Operadores', 'Usuários Básicos']
            )
    except Group.DoesNotExist:
        pass
    
    return allowed_groups


def get_manageable_users_queryset(current_user):
    """
    Retorna um queryset com os usuários que o usuário atual pode gerenciar.
    Aplica as regras de hierarquia para filtrar apenas usuários visíveis/editáveis.
    """
    current_level = get_user_level(current_user)
    
    if current_level == 'admin_principal':
        # Admin principal pode gerenciar todos exceto ele mesmo e o ID=1 (se não for ele)
        return User.objects.exclude(id=current_user.id).exclude(
            id=1 if current_user.id != 1 else None
        )
    
    elif current_level == 'administrador':
        # Administradores podem gerenciar gerentes, operadores e usuários básicos
        # Excluindo: admin principal (ID=1), outros administradores, e ele mesmo
        return User.objects.exclude(id=1).exclude(
            id=current_user.id
        ).exclude(
            groups__name='Administradores'
        ).exclude(
            is_superuser=True
        ).distinct()
    
    elif current_level == 'gerente':
        # Gerentes podem gerenciar apenas operadores e usuários básicos
        # Excluindo: admin principal, administradores, outros gerentes, e ele mesmo
        excluded_groups = ['Administradores', 'Gerentes']
        return User.objects.exclude(id=1).exclude(
            id=current_user.id
        ).exclude(
            groups__name__in=excluded_groups
        ).exclude(
            is_superuser=True
        ).exclude(
            is_staff=True
        ).distinct()
    
    else:
        # Operadores e usuários básicos não podem gerenciar ninguém
        return User.objects.none()


def validate_user_form_submission(current_user, target_user, form_data):
    """
    Valida se o formulário de usuário pode ser submetido com os dados fornecidos.
    Retorna (is_valid, error_messages)
    """
    errors = []
    current_level = get_user_level(current_user)
    
    # Se estiver editando, verificar se pode editar
    if target_user and not can_edit_user(current_user, target_user):
        errors.append('Você não tem permissão para editar este usuário.')
        return False, errors
    
    # Verificar grupos selecionados
    if 'groups' in form_data:
        selected_groups = form_data['groups']
        if not can_change_user_groups(current_user, target_user, selected_groups):
            errors.append('Você não pode atribuir esses grupos ao usuário.')
    
    # Verificar flags de sistema (is_staff, is_superuser)
    if form_data.get('is_superuser') and current_level != 'admin_principal':
        errors.append('Apenas o administrador principal pode criar superusuários.')
    
    if form_data.get('is_staff') and current_level not in ['admin_principal', 'administrador']:
        errors.append('Apenas administradores podem dar acesso ao painel admin.')
    
    # Admin principal (ID=1) não pode ter flags alteradas
    if target_user and target_user.id == 1:
        if not form_data.get('is_superuser', True):
            errors.append('O administrador principal deve manter o status de superusuário.')
        if not form_data.get('is_active', True):
            errors.append('O administrador principal deve permanecer ativo.')
    
    return len(errors) == 0, errors


def get_user_level_display(user):
    """
    Retorna o nome amigável do nível do usuário.
    """
    level = get_user_level(user)
    
    display_names = {
        'admin_principal': 'Administrador Principal',
        'administrador': 'Administrador',
        'gerente': 'Gerente',
        'operador': 'Operador',
        'usuario_basico': 'Usuário Básico'
    }
    
    return display_names.get(level, 'Usuário Básico')


def is_protected_user(user):
    """
    Verifica se um usuário está protegido contra alterações críticas.
    """
    return user.id == 1 and user.is_superuser


def should_show_admin_menu(user):
    """
    Verifica se deve mostrar o menu de administração para o usuário.
    Apenas gerentes e administradores veem o menu administrativo.
    """
    return can_access_user_management(user)


def should_show_user_management_link(user):
    """
    Verifica se deve mostrar o link de gerenciamento de usuários no menu.
    """
    return can_access_user_management(user)


def get_max_user_level_can_create(current_user):
    """
    Retorna o nível máximo de usuário que o usuário atual pode criar.
    """
    current_level = get_user_level(current_user)
    
    if current_level == 'admin_principal':
        return 'administrador'  # Pode criar até administradores
    elif current_level == 'administrador':
        return 'gerente'  # Pode criar até gerentes
    elif current_level == 'gerente':
        return 'operador'  # Pode criar até operadores
    else:
        return None  # Não pode criar usuários


def can_access_admin_panel(user):
    """
    Verifica se o usuário pode acessar o painel administrativo do Django (/admin/).
    Apenas usuários com is_staff=True podem acessar.
    """
    return user.is_authenticated and user.is_staff


def get_user_permissions_summary(user):
    """
    Retorna um resumo das permissões do usuário para exibição.
    """
    level = get_user_level(user)
    level_display = get_user_level_display(user)
    
    permissions = {
        'level': level,
        'level_display': level_display,
        'can_access_user_management': can_access_user_management(user),
        'can_access_admin_panel': can_access_admin_panel(user),
        'max_user_level_can_create': get_max_user_level_can_create(user),
        'is_protected': is_protected_user(user),
        'groups': list(user.groups.values_list('name', flat=True)) if user.is_authenticated else []
    }
    
    return permissions


def validate_group_assignment(current_user, target_groups):
    """
    Valida se o usuário atual pode atribuir os grupos especificados.
    Retorna (is_valid, error_message)
    """
    current_level = get_user_level(current_user)
    
    # Verificar cada grupo
    for group in target_groups:
        group_name = group.name if hasattr(group, 'name') else str(group)
        
        if group_name == 'Administradores' and current_level != 'admin_principal':
            return False, "Apenas o Administrador Principal pode criar Administradores"
        
        if group_name == 'Gerentes' and current_level not in ['admin_principal', 'administrador']:
            return False, "Apenas Administradores podem criar Gerentes"
        
        if group_name == 'Operadores' and current_level not in ['admin_principal', 'administrador', 'gerente']:
            return False, "Você não tem permissão para criar Operadores"
    
    return True, None


# Constantes para facilitar o uso
USER_LEVELS = {
    'ADMIN_PRINCIPAL': 'admin_principal',
    'ADMINISTRADOR': 'administrador', 
    'GERENTE': 'gerente',
    'OPERADOR': 'operador',
    'USUARIO_BASICO': 'usuario_basico'
}

GROUP_NAMES = {
    'ADMINISTRADORES': 'Administradores',
    'GERENTES': 'Gerentes',
    'OPERADORES': 'Operadores',
    'USUARIOS_BASICOS': 'Usuários Básicos'
}

# ====================================
# FUNÇÕES PARA GERENCIAMENTO DE GRUPOS
# ====================================

def can_manage_group(current_user, group):
    """
    Verifica se o usuário atual pode gerenciar (visualizar) um grupo específico.
    """
    current_level = get_user_level(current_user)
    
    # Admin principal pode gerenciar todos os grupos
    if current_level == 'admin_principal':
        return True
    
    # Administradores podem gerenciar grupos não-administrativos
    if current_level == 'administrador':
        return group.name != 'Administradores'
    
    # Gerentes podem gerenciar apenas grupos de nível inferior
    if current_level == 'gerente':
        return group.name in ['Operadores', 'Usuários Básicos']
    
    # Outros não podem gerenciar grupos
    return False


def can_view_group(current_user, group):
    """
    Verifica se o usuário atual pode visualizar detalhes de um grupo específico.
    """
    # Mesma lógica de can_manage_group - se pode gerenciar, pode visualizar
    return can_manage_group(current_user, group)


def can_create_group(current_user):
    """
    Verifica se o usuário atual pode criar novos grupos.
    """
    current_level = get_user_level(current_user)
    
    # Apenas gerentes e acima podem criar grupos
    return current_level in ['admin_principal', 'administrador', 'gerente']


def can_edit_group(current_user, group):
    """
    Verifica se o usuário atual pode editar um grupo específico.
    """
    current_level = get_user_level(current_user)
    
    # Verificar se pode gerenciar o grupo
    if not can_manage_group(current_user, group):
        return False
    
    # Grupos protegidos têm restrições especiais
    if is_protected_group(group):
        # Apenas admin principal pode editar grupos de administradores
        if group.name == 'Administradores':
            return current_level == 'admin_principal'
        
        # Administradores e acima podem editar outros grupos protegidos
        return current_level in ['admin_principal', 'administrador']
    
    # Grupos não-protegidos seguem regras normais de gerenciamento
    return True


def can_delete_group(current_user, group):
    """
    Verifica se o usuário atual pode deletar um grupo específico.
    """
    current_level = get_user_level(current_user)
    
    # Grupos protegidos não podem ser deletados
    if is_protected_group(group):
        return False
    
    # Verificar se pode gerenciar o grupo
    if not can_manage_group(current_user, group):
        return False
    
    # Admin principal pode deletar qualquer grupo não-protegido
    if current_level == 'admin_principal':
        return True
    
    # Administradores podem deletar grupos de nível inferior
    if current_level == 'administrador':
        return group.name not in ['Administradores', 'Gerentes']
    
    # Gerentes podem deletar apenas grupos que criaram ou de nível muito inferior
    if current_level == 'gerente':
        # Verificar se o grupo foi criado por um gerente (não é grupo padrão do sistema)
        return group.name not in ['Administradores', 'Gerentes', 'Operadores', 'Usuários Básicos']
    
    return False


def can_assign_permission_to_group(current_user, group, permission):
    """
    Verifica se o usuário atual pode atribuir uma permissão específica a um grupo.
    """
    current_level = get_user_level(current_user)
    
    # Verificar se pode editar o grupo
    if not can_edit_group(current_user, group):
        return False
    
    # Admin principal pode atribuir qualquer permissão
    if current_level == 'admin_principal':
        return True
    
    # Permissões críticas que apenas admin principal pode atribuir
    critical_permissions = [
        'auth.add_user', 'auth.change_user', # 'auth.delete_user',  # REMOVIDO
        'auth.add_group', 'auth.change_group', 'auth.delete_group',
        'auth.add_permission', 'auth.change_permission', 'auth.delete_permission'
    ]
    
    permission_codename = f"{permission.content_type.app_label}.{permission.codename}"
    
    if permission_codename in critical_permissions and current_level != 'admin_principal':
        return False
    
    # Administradores podem atribuir a maioria das permissões
    if current_level == 'administrador':
        # Não podem dar permissões de superusuário
        if permission.codename == 'add_user' and group.name == 'Administradores':
            return False
        return True
    
    # Gerentes podem atribuir apenas permissões básicas
    if current_level == 'gerente':
        basic_permissions = [
            'auth.view_user',
            # Adicionar outras conforme necessário
        ]
        return permission_codename in basic_permissions
    
    return False


def get_manageable_groups_queryset(current_user):
    """
    Retorna um queryset com os grupos que o usuário atual pode gerenciar.
    
    IMPORTANTE: Esta função NÃO deve usar .union() para evitar conflitos
    com .prefetch_related() nas views.
    """
    current_level = get_user_level(current_user)
    
    if current_level == 'admin_principal':
        # Admin principal pode gerenciar todos os grupos
        return Group.objects.all().order_by('name')
    
    elif current_level == 'administrador':
        # Administradores podem gerenciar todos exceto grupo de administradores
        return Group.objects.exclude(name='Administradores').order_by('name')
    
    elif current_level == 'gerente':
        # Gerentes podem gerenciar apenas grupos de nível inferior e grupos customizados
        # Usando exclude() em vez de union() para compatibilidade com prefetch_related()
        return Group.objects.exclude(
            name__in=['Administradores', 'Gerentes']
        ).order_by('name')
    
    else:
        # Outros níveis não podem gerenciar grupos
        return Group.objects.none()


def is_protected_group(group):
    """
    Verifica se um grupo é protegido (grupos básicos do sistema).
    """
    protected_groups = ['Administradores', 'Gerentes', 'Operadores', 'Usuários Básicos']
    return group.name in protected_groups


def validate_group_form_submission(current_user, target_group, form_data):
    """
    Valida se o formulário de grupo pode ser submetido com os dados fornecidos.
    Retorna (is_valid, error_messages)
    """
    errors = []
    current_level = get_user_level(current_user)
    
    # Se estiver editando, verificar se pode editar
    if target_group and not can_edit_group(current_user, target_group):
        errors.append('Você não tem permissão para editar este grupo.')
        return False, errors
    
    # Verificar permissões selecionadas
    if 'permissions' in form_data:
        selected_permissions = form_data['permissions']
        for permission in selected_permissions:
            if not can_assign_permission_to_group(current_user, target_group or Group(name=form_data.get('name', '')), permission):
                errors.append(f'Você não pode atribuir a permissão "{permission.name}" a este grupo.')
    
    # Verificar se está tentando criar grupo com nome protegido
    if not target_group:  # Criação de novo grupo
        group_name = form_data.get('name', '')
        if is_protected_group(Group(name=group_name)) and current_level != 'admin_principal':
            errors.append('Apenas o administrador principal pode criar grupos com nomes protegidos.')
    
    return len(errors) == 0, errors


def get_group_creation_level_limit(current_user):
    """
    Retorna o nível máximo de grupo que o usuário atual pode criar.
    """
    current_level = get_user_level(current_user)
    
    if current_level == 'admin_principal':
        return 'administrador'
    elif current_level == 'administrador':
        return 'gerente'
    elif current_level == 'gerente':
        return 'operador'
    else:
        return None
