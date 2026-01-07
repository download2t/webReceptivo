"""
Views para gerenciamento completo de grupos (cargos/funções).
Permite criar, editar, excluir e configurar permissões dos grupos dinamicamente.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django import forms
from django.contrib.contenttypes.models import ContentType
from .permission_helpers import (
    can_access_user_management, get_user_level, get_user_level_display,
    can_manage_group, can_create_group, can_edit_group, can_delete_group,
    can_assign_permission_to_group, get_manageable_groups_queryset,
    validate_group_form_submission, is_protected_group
)

# Decorador para gerenciamento de grupos
def group_management_required(view_func):
    """Decorador que verifica se o usuário pode acessar o gerenciamento de grupos"""
    def _wrapped_view(request, *args, **kwargs):
        if not can_access_user_management(request.user):
            messages.error(request, 'Você não tem permissão para gerenciar grupos.')
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class GroupManagementForm(forms.ModelForm):
    """Formulário para gerenciamento de grupos"""
    
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Permissões do Grupo'
    )
    
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do grupo/cargo'
            }),
        }
        labels = {
            'name': 'Nome do Grupo/Cargo',
        }
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        self.is_editing = kwargs.pop('is_editing', False)
        self.is_protected = kwargs.pop('is_protected', False)
        
        # Para edição, definir valores iniciais
        if self.is_editing and 'instance' in kwargs and kwargs['instance'].pk:
            instance = kwargs['instance']
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            kwargs['initial']['permissions'] = list(instance.permissions.values_list('pk', flat=True))
        
        super().__init__(*args, **kwargs)
        
        # Filtrar permissões disponíveis baseado no usuário atual
        if self.current_user:
            available_permissions = self.get_available_permissions()
            
            # Se estiver editando, incluir permissões atuais do grupo mesmo que não sejam "disponíveis"
            # Isso garante que as permissões já atribuídas apareçam no formulário
            if self.is_editing and self.instance and self.instance.pk:
                current_perms = self.instance.permissions.all()
                available_permissions = available_permissions | Permission.objects.filter(pk__in=current_perms.values_list('pk'))
            
            self.fields['permissions'].queryset = available_permissions
            
        # Proteção para grupos especiais
        if self.is_protected:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].help_text = 'Nome de grupo protegido não pode ser alterado'
            
    def get_available_permissions(self):
        """Retorna permissões que o usuário atual pode atribuir a grupos"""
        user_level = get_user_level(self.current_user)
        
        if user_level == 'admin_principal':
            # Admin principal pode atribuir qualquer permissão
            return Permission.objects.all()
        elif user_level == 'administrador':
            # Administradores podem atribuir a maioria das permissões, exceto algumas críticas
            excluded_permissions = [
                'auth.add_permission',
                'auth.change_permission', 
                'auth.delete_permission',
                'contenttypes.add_contenttype',
                'contenttypes.change_contenttype',
                'contenttypes.delete_contenttype',
            ]
            return Permission.objects.exclude(
                Q(content_type__app_label='auth', codename__in=['add_permission', 'change_permission', 'delete_permission']) |
                Q(content_type__app_label='contenttypes')
            )
        elif user_level == 'gerente':
            # Gerentes podem atribuir apenas permissões básicas
            allowed_permissions = [
                'auth.view_user',
                # Adicionar outras permissões conforme necessário
            ]
            return Permission.objects.filter(
                Q(content_type__app_label='auth', codename='view_user')
            )
        else:
            # Outros níveis não podem atribuir permissões
            return Permission.objects.none()
    
    def clean_name(self):
        name = self.cleaned_data['name']
        
        # Verificar se não está tentando criar grupos protegidos
        protected_names = ['Administradores', 'Gerentes', 'Operadores', 'Usuários Básicos']
        
        if not self.is_editing and name in protected_names:
            raise forms.ValidationError('Este nome de grupo é protegido e não pode ser usado.')
            
        # Verificar duplicatas (exceto na edição do próprio grupo)
        existing = Group.objects.filter(name=name)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError('Já existe um grupo com este nome.')
            
        return name
    
    def save(self, commit=True):
        group = super().save(commit=False)
        
        if commit:
            group.save()
            
            # Salvar permissões
            permissions = self.cleaned_data.get('permissions')
            if permissions is not None:
                group.permissions.set(permissions)
        
        return group


@login_required
@group_management_required
def group_list(request):
    """
    Lista grupos que o usuário atual pode gerenciar.
    """
    
    # Obter apenas grupos que o usuário atual pode gerenciar
    groups = get_manageable_groups_queryset(request.user).prefetch_related('permissions')
    
    # Filtros
    search = request.GET.get('search', '')
    
    if search:
        groups = groups.filter(name__icontains=search)
    
    # Ordenação
    order_by = request.GET.get('order_by', 'name')
    groups = groups.order_by(order_by)
    
    # Paginação
    paginator = Paginator(groups, 20)  # 20 grupos por página
    page_number = request.GET.get('page')
    groups_page = paginator.get_page(page_number)
    
    # Adicionar informações de permissão para cada grupo
    for group in groups_page:
        group.can_edit = can_edit_group(request.user, group)
        group.can_delete = can_delete_group(request.user, group)
        group.is_protected = is_protected_group(group)
        group.permission_count = group.permissions.count()
    
    context = {
        'groups': groups_page,
        'search': search,
        'order_by': order_by,
        'current_user_level': get_user_level_display(request.user),
        'can_create_group': can_create_group(request.user),
        'total_groups': get_manageable_groups_queryset(request.user).count(),
    }
    
    return render(request, 'user_management/group_list.html', context)


@login_required
@group_management_required
def group_create(request):
    """
    Criar novo grupo/cargo.
    """
    
    if not can_create_group(request.user):
        messages.error(request, 'Você não tem permissão para criar grupos.')
        return redirect('user_management:group_list')
    
    if request.method == 'POST':
        form = GroupManagementForm(
            request.POST,
            current_user=request.user,
            is_editing=False
        )
        
        if form.is_valid():
            # Validação adicional de permissões
            is_valid, errors = validate_group_form_submission(
                request.user,
                None,  # Novo grupo
                form.cleaned_data
            )
            
            if not is_valid:
                for error in errors:
                    form.add_error(None, error)
            else:
                group = form.save()
                messages.success(request, f'Grupo "{group.name}" criado com sucesso!')
                return redirect('user_management:group_detail', pk=group.pk)
    else:
        form = GroupManagementForm(current_user=request.user, is_editing=False)
    
    context = {
        'form': form,
        'title': 'Criar Novo Grupo/Cargo',
        'button_text': 'Criar Grupo',
        'current_user_level': get_user_level_display(request.user)
    }
    
    return render(request, 'user_management/group_form.html', context)


@login_required
@group_management_required
def group_edit(request, pk):
    """
    Editar grupo existente.
    """
    
    group = get_object_or_404(Group, pk=pk)
    
    # Verificar se pode editar este grupo
    if not can_edit_group(request.user, group):
        messages.error(request, 'Você não tem permissão para editar este grupo.')
        return redirect('user_management:group_list')
    
    is_protected = is_protected_group(group)
    
    if request.method == 'POST':
        form = GroupManagementForm(
            request.POST,
            instance=group,
            current_user=request.user,
            is_editing=True,
            is_protected=is_protected
        )
        
        if form.is_valid():
            # Validação adicional de permissões
            is_valid, errors = validate_group_form_submission(
                request.user,
                group,
                form.cleaned_data
            )
            
            if not is_valid:
                for error in errors:
                    form.add_error(None, error)
            else:
                saved_group = form.save()
                messages.success(request, f'Grupo "{saved_group.name}" atualizado com sucesso!')
                return redirect('user_management:group_detail', pk=saved_group.pk)
    else:
        form = GroupManagementForm(
            instance=group,
            current_user=request.user,
            is_editing=True,
            is_protected=is_protected
        )
    
    context = {
        'form': form,
        'group_obj': group,
        'title': f'Editar Grupo: {group.name}',
        'button_text': 'Salvar Alterações',
        'current_user_level': get_user_level_display(request.user),
        'is_protected': is_protected
    }
    
    return render(request, 'user_management/group_form.html', context)


@login_required
@group_management_required
def group_detail(request, pk):
    """
    Visualizar detalhes do grupo.
    """
    
    group = get_object_or_404(Group, pk=pk)
    
    # Verificar se pode visualizar este grupo
    if not can_manage_group(request.user, group):
        messages.error(request, 'Você não tem permissão para visualizar este grupo.')
        return redirect('user_management:group_list')
    
    # Organizar permissões por aplicação
    permissions_by_app = {}
    for permission in group.permissions.select_related('content_type').order_by('content_type__app_label', 'name'):
        app_label = permission.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(permission)
    
    # Usuários neste grupo
    users_in_group = group.user_set.all()[:10]  # Primeiros 10 usuários
    total_users = group.user_set.count()
    
    context = {
        'group_obj': group,
        'permissions_by_app': permissions_by_app,
        'users_in_group': users_in_group,
        'total_users': total_users,
        'current_user_level': get_user_level_display(request.user),
        'can_edit': can_edit_group(request.user, group),
        'can_delete': can_delete_group(request.user, group),
        'is_protected': is_protected_group(group),
    }
    
    return render(request, 'user_management/group_detail.html', context)


@login_required
@group_management_required
def group_delete(request, pk):
    """
    Deletar grupo (com confirmação).
    """
    
    group = get_object_or_404(Group, pk=pk)
    
    # Verificar se pode deletar este grupo
    if not can_delete_group(request.user, group):
        messages.error(request, 'Você não tem permissão para deletar este grupo.')
        return redirect('user_management:group_detail', pk=pk)
    
    # Verificar se é grupo protegido
    if is_protected_group(group):
        messages.error(request, 'Este grupo é protegido e não pode ser deletado.')
        return redirect('user_management:group_detail', pk=pk)
    
    if request.method == 'POST':
        group_name = group.name
        users_count = group.user_set.count()
        
        # Remover usuários do grupo antes de deletar
        group.user_set.clear()
        group.delete()
        
        messages.success(request, 
            f'Grupo "{group_name}" deletado com sucesso. '
            f'{users_count} usuário(s) foram removidos do grupo.'
        )
        return redirect('user_management:group_list')
    
    # Informações sobre o impacto da deleção
    users_affected = group.user_set.all()
    
    context = {
        'group_obj': group,
        'title': f'Deletar Grupo: {group.name}',
        'users_affected': users_affected,
        'users_count': users_affected.count(),
    }
    
    return render(request, 'user_management/group_delete.html', context)
