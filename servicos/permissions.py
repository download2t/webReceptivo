"""
Sistema de Permissões para WebReceptivo

Este módulo centraliza todas as verificações de permissões do sistema.

PERMISSÕES DISPONÍVEIS (Django built-in):
- add_<model>: Criar novos registros
- view_<model>: Visualizar registros
- change_<model>: Editar registros
- delete_<model>: Deletar registros

MODELS COM PERMISSÕES:
- categoria (Categoria)
- subcategoria (SubCategoria/Serviços)
- transfer (Transfer)
- tipomeiaentrada (TipoMeiaEntrada/Meia Entrada)
- ordemservico (OrdemServico/Ordem de Serviço)
- lancamentoservico (LancamentoServico)
- transferos (TransferOS)

HIERARQUIA DE PERMISSÕES:
1. Superusuários (is_superuser=True): Acesso total
2. Permissões individuais do usuário: Sobrescrevem permissões do grupo
3. Permissões do grupo: Aplicadas se usuário não tem permissão individual

COMO USAR:

1. Em views baseadas em função:
   from servicos.permissions import require_permission
   
   @require_permission('servicos.view_categoria')
   def categoria_list(request):
       ...
   
   @require_permission('servicos.add_categoria')
   def categoria_create(request):
       ...

2. Em views baseadas em classe:
   from servicos.permissions import PermissionRequiredMixin
   
   class CategoriaListView(PermissionRequiredMixin, ListView):
       permission_required = 'servicos.view_categoria'
       ...

3. Verificação condicional em templates:
   {% if perms.servicos.add_categoria %}
       <a href="...">Nova Categoria</a>
   {% endif %}

4. Verificação programática:
   if request.user.has_perm('servicos.change_categoria'):
       # Permite edição
       ...
"""

from functools import wraps
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin as DjangoPermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def require_permission(perm, raise_exception=False):
    """
    Decorator para verificar permissões em function-based views.
    
    Args:
        perm (str): Permissão requerida no formato 'app.permission_model'
                   Ex: 'servicos.view_categoria'
        raise_exception (bool): Se True, levanta PermissionDenied. 
                               Se False, redireciona com mensagem.
    
    Uso:
        @require_permission('servicos.add_categoria')
        def categoria_create(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # Superusuários têm acesso total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verifica permissão (individual ou do grupo)
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            
            # Sem permissão
            if raise_exception:
                raise PermissionDenied(
                    f"Você não tem permissão para realizar esta ação. "
                    f"Permissão necessária: {perm}"
                )
            
            messages.error(
                request, 
                f"Você não tem permissão para acessar esta página. "
                f"Entre em contato com o administrador."
            )
            return redirect('core:dashboard')
        
        return wrapped_view
    return decorator


class PermissionRequiredMixin(DjangoPermissionRequiredMixin):
    """
    Mixin para class-based views que requer permissões.
    
    Attributes:
        permission_required (str or list): Permissão(ões) necessária(s)
        raise_exception (bool): Se True, levanta PermissionDenied
    
    Uso:
        class CategoriaCreateView(PermissionRequiredMixin, CreateView):
            permission_required = 'servicos.add_categoria'
            model = Categoria
            ...
        
        class CategoriaUpdateView(PermissionRequiredMixin, UpdateView):
            permission_required = ['servicos.view_categoria', 'servicos.change_categoria']
            model = Categoria
            ...
    """
    raise_exception = False
    
    def has_permission(self):
        """
        Sobrescreve método padrão para adicionar suporte a superusuários
        e melhorar mensagens de erro.
        """
        # Superusuários têm acesso total
        if self.request.user.is_superuser:
            return True
        
        # Verifica permissões normalmente
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms)
    
    def handle_no_permission(self):
        """Customiza comportamento quando usuário não tem permissão."""
        if not self.raise_exception:
            messages.error(
                self.request,
                "Você não tem permissão para acessar esta página. "
                "Entre em contato com o administrador."
            )
            return redirect('core:dashboard')
        
        return super().handle_no_permission()


def check_object_permission(user, obj, permission_type):
    """
    Verifica se usuário tem permissão para operar em objeto específico.
    
    Args:
        user: Usuário Django
        obj: Instância do model
        permission_type (str): Tipo de permissão ('view', 'change', 'delete')
    
    Returns:
        bool: True se tem permissão, False caso contrário
    
    Uso:
        categoria = get_object_or_404(Categoria, pk=pk)
        if not check_object_permission(request.user, categoria, 'change'):
            messages.error(request, "Sem permissão para editar esta categoria")
            return redirect('servicos:categoria_list')
    """
    # Superusuários têm acesso total
    if user.is_superuser:
        return True
    
    # Monta nome da permissão
    app_label = obj._meta.app_label
    model_name = obj._meta.model_name
    perm = f'{app_label}.{permission_type}_{model_name}'
    
    # Verifica permissão
    return user.has_perm(perm)


# ==================== GRUPOS DE PERMISSÕES PADRÃO ====================

GRUPOS_PERMISSOES = {
    'Administradores': {
        'descricao': 'Administradores têm controle total de usuários e acesso completo ao sistema',
        'permissoes': [
            # Permissões de usuários e grupos (já existentes)
            'auth.add_group',
            'auth.change_group',
            'auth.view_group',
            'auth.add_user',
            'auth.change_user',
            'auth.delete_user',
            'auth.view_user',
            
            # NOVAS: Módulo de Serviços - Acesso completo
            'servicos.view_categoria',
            'servicos.add_categoria',
            'servicos.change_categoria',
            'servicos.delete_categoria',
            
            'servicos.view_subcategoria',
            'servicos.add_subcategoria',
            'servicos.change_subcategoria',
            'servicos.delete_subcategoria',
            
            'servicos.view_transfer',
            'servicos.add_transfer',
            'servicos.change_transfer',
            'servicos.delete_transfer',
            
            'servicos.view_tipomeiaentrada',
            'servicos.add_tipomeiaentrada',
            'servicos.change_tipomeiaentrada',
            'servicos.delete_tipomeiaentrada',
            
            'servicos.view_ordemservico',
            'servicos.add_ordemservico',
            'servicos.change_ordemservico',
            'servicos.delete_ordemservico',
            
            'servicos.view_lancamentoservico',
            'servicos.add_lancamentoservico',
            'servicos.change_lancamentoservico',
            'servicos.delete_lancamentoservico',
            
            'servicos.view_transferos',
            'servicos.add_transferos',
            'servicos.change_transferos',
            'servicos.delete_transferos',
        ]
    },
    
    'Gerentes': {
        'descricao': 'Gerentes podem gerenciar usuários e têm acesso completo aos serviços',
        'permissoes': [
            # Permissões de usuários (já existentes)
            'auth.view_group',
            'auth.add_user',
            'auth.change_user',
            'auth.view_user',
            
            # NOVAS: Módulo de Serviços - Acesso completo
            'servicos.view_categoria',
            'servicos.add_categoria',
            'servicos.change_categoria',
            'servicos.delete_categoria',
            
            'servicos.view_subcategoria',
            'servicos.add_subcategoria',
            'servicos.change_subcategoria',
            'servicos.delete_subcategoria',
            
            'servicos.view_transfer',
            'servicos.add_transfer',
            'servicos.change_transfer',
            'servicos.delete_transfer',
            
            'servicos.view_tipomeiaentrada',
            'servicos.add_tipomeiaentrada',
            'servicos.change_tipomeiaentrada',
            'servicos.delete_tipomeiaentrada',
            
            'servicos.view_ordemservico',
            'servicos.add_ordemservico',
            'servicos.change_ordemservico',
            'servicos.delete_ordemservico',
            
            'servicos.view_lancamentoservico',
            'servicos.add_lancamentoservico',
            'servicos.change_lancamentoservico',
            'servicos.delete_lancamentoservico',
            
            'servicos.view_transferos',
            'servicos.add_transferos',
            'servicos.change_transferos',
            'servicos.delete_transferos',
        ]
    },
    
    'Operadores': {
        'descricao': 'Operadores podem criar e gerenciar ordens de serviço e visualizar cadastros',
        'permissoes': [
            # NOVAS: Visualização de cadastros
            'servicos.view_categoria',
            'servicos.view_subcategoria',
            'servicos.view_transfer',
            'servicos.view_tipomeiaentrada',
            
            # NOVAS: CRUD completo de Ordens de Serviço
            'servicos.view_ordemservico',
            'servicos.add_ordemservico',
            'servicos.change_ordemservico',
            'servicos.delete_ordemservico',
            
            'servicos.view_lancamentoservico',
            'servicos.add_lancamentoservico',
            'servicos.change_lancamentoservico',
            'servicos.delete_lancamentoservico',
            
            'servicos.view_transferos',
            'servicos.add_transferos',
            'servicos.change_transferos',
            'servicos.delete_transferos',
        ]
    },
    
    'Usuários Básicos': {
        'descricao': 'Usuários básicos podem apenas visualizar informações',
        'permissoes': [
            # NOVAS: Apenas visualização
            'servicos.view_categoria',
            'servicos.view_subcategoria',
            'servicos.view_transfer',
            'servicos.view_tipomeiaentrada',
            'servicos.view_ordemservico',
            'servicos.view_lancamentoservico',
            'servicos.view_transferos',
        ]
    },
}


def criar_grupos_permissoes():
    """
    Cria os grupos padrão com suas permissões.
    
    Execute este comando para criar/atualizar os grupos:
        python manage.py shell
        >>> from servicos.permissions import criar_grupos_permissoes
        >>> criar_grupos_permissoes()
    
    Ou crie um management command (recomendado para produção).
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    
    grupos_criados = []
    
    for nome_grupo, config in GRUPOS_PERMISSOES.items():
        # Cria ou obtém o grupo
        grupo, created = Group.objects.get_or_create(name=nome_grupo)
        
        # Limpa permissões existentes
        grupo.permissions.clear()
        
        # Adiciona permissões
        for perm_string in config['permissoes']:
            app_label, codename = perm_string.split('.')
            
            try:
                permission = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename
                )
                grupo.permissions.add(permission)
            except Permission.DoesNotExist:
                print(f"⚠️  Permissão não encontrada: {perm_string}")
        
        status = "criado" if created else "atualizado"
        grupos_criados.append(f"✅ Grupo '{nome_grupo}' {status} com {grupo.permissions.count()} permissões")
    
    return "\n".join(grupos_criados)


def listar_permissoes_usuario(user):
    """
    Lista todas as permissões de um usuário (individuais + grupos).
    
    Uso:
        from servicos.permissions import listar_permissoes_usuario
        print(listar_permissoes_usuario(request.user))
    """
    if user.is_superuser:
        return "👑 SUPERUSUÁRIO - Acesso total a tudo"
    
    # Permissões individuais
    user_perms = user.user_permissions.all()
    
    # Permissões dos grupos
    group_perms = Permission.objects.filter(group__user=user)
    
    # Todas as permissões efetivas
    all_perms = user.get_all_permissions()
    
    output = []
    output.append(f"👤 Usuário: {user.get_full_name() or user.username}")
    output.append(f"📋 Grupos: {', '.join([g.name for g in user.groups.all()]) or 'Nenhum'}")
    output.append(f"\n🔑 Total de permissões: {len(all_perms)}")
    
    if user_perms.exists():
        output.append(f"\n⭐ Permissões individuais ({user_perms.count()}):")
        for perm in user_perms:
            output.append(f"   - {perm.content_type.app_label}.{perm.codename}")
    
    if group_perms.exists():
        output.append(f"\n👥 Permissões dos grupos ({group_perms.count()}):")
        for perm in group_perms.distinct():
            grupos = [g.name for g in Group.objects.filter(permissions=perm, user=user)]
            output.append(f"   - {perm.content_type.app_label}.{perm.codename} (via {', '.join(grupos)})")
    
    return "\n".join(output)
