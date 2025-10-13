from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django import forms
from accounts.models import UserProfile
from .permission_helpers import (
    can_access_user_management, can_view_user, can_edit_user,
    can_create_user_with_level, can_change_user_groups, get_manageable_users_queryset,
    get_user_level, get_allowed_groups_for_user, validate_user_form_submission,
    is_protected_user, get_user_level_display, validate_group_assignment
)
import json

User = get_user_model()


class UserManagementForm(forms.ModelForm):
    """Formulário para gerenciamento de usuários"""
    
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha'
        }),
        required=False,
        help_text='Deixe em branco para manter a senha atual (apenas na edição)'
    )
    
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        }),
        required=False
    )
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Grupos de Usuário'
    )
    
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Permissões Individuais'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Nome de Usuário',
            'email': 'E-mail',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'is_active': 'Usuário Ativo',
            'is_staff': 'Acesso ao Admin',
            'is_superuser': 'Super Usuário',
        }
    
    def __init__(self, *args, **kwargs):
        self.is_editing = kwargs.pop('is_editing', False)
        self.is_protected_admin = kwargs.pop('is_protected_admin', False)
        self.current_user = kwargs.pop('current_user', None)
        
        # Para edição, definir valores iniciais antes do super() para CheckboxSelectMultiple
        if self.is_editing and 'instance' in kwargs and kwargs['instance'].pk:
            instance = kwargs['instance']
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            # Usar IDs dos grupos e permissões para o widget CheckboxSelectMultiple
            kwargs['initial']['groups'] = list(instance.groups.values_list('pk', flat=True))
            kwargs['initial']['user_permissions'] = list(instance.user_permissions.values_list('pk', flat=True))
        
        super().__init__(*args, **kwargs)
        
        # Filtrar grupos disponíveis baseado nas permissões do usuário atual
        if self.current_user:
            allowed_groups = get_allowed_groups_for_user(self.current_user)
            self.fields['groups'].queryset = allowed_groups
            
            # Filtrar permissões baseado no nível do usuário
            current_level = get_user_level(self.current_user)
            if current_level not in ['admin_principal', 'administrador']:
                # Gerentes e abaixo não podem definir permissões individuais
                self.fields['user_permissions'].widget = forms.HiddenInput()
                self.fields['user_permissions'].required = False
            
            # Apenas admin principal pode criar superusuários
            if current_level != 'admin_principal':
                if not self.is_editing or not self.instance.is_superuser:
                    self.fields['is_superuser'].widget.attrs['disabled'] = True
                    self.fields['is_superuser'].help_text = 'Apenas o administrador principal pode criar superusuários'
            
            # Apenas administradores e admin principal podem dar acesso ao admin
            if current_level not in ['admin_principal', 'administrador']:
                if not self.is_editing or not self.instance.is_staff:
                    self.fields['is_staff'].widget.attrs['disabled'] = True
                    self.fields['is_staff'].help_text = 'Apenas administradores podem dar acesso ao painel admin'
        
        # Se estiver editando, configurações adicionais
        if self.is_editing and self.instance.pk:
            self.fields['password1'].help_text = 'Deixe em branco para manter a senha atual'
            
            # Proteção para admin principal
            if self.is_protected_admin:
                self.fields['is_superuser'].widget.attrs['readonly'] = True
                self.fields['is_superuser'].help_text = 'Administrador principal não pode ter este status removido'
                self.fields['is_active'].widget.attrs['readonly'] = True
                self.fields['is_active'].help_text = 'Administrador principal deve permanecer ativo'
                self.fields['username'].widget.attrs['readonly'] = True
                self.fields['username'].help_text = 'Nome de usuário do administrador principal não pode ser alterado'
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['password1'].help_text = 'Mínimo 8 caracteres'
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('As senhas não coincidem.')
        elif password1 and not password2:
            raise forms.ValidationError('Confirme a senha.')
        
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
            
            # Salvar grupos manualmente - IMPORTANTE para funcionar corretamente
            groups = self.cleaned_data.get('groups')
            if groups is not None:
                user.groups.set(groups)
            
            # Salvar permissões individuais manualmente
            user_permissions = self.cleaned_data.get('user_permissions')
            if user_permissions is not None:
                user.user_permissions.set(user_permissions)
            
            # Criar perfil se não existir
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)
        
        return user


# Decorador customizado para verificar acesso ao gerenciamento de usuários
def user_management_required(view_func):
    """Decorador que verifica se o usuário pode acessar o gerenciamento de usuários"""
    def _wrapped_view(request, *args, **kwargs):
        if not can_access_user_management(request.user):
            messages.error(request, 'Você não tem permissão para acessar esta área.')
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@user_management_required
def user_list(request):
    """
    Lista usuários que o usuário atual pode gerenciar, aplicando filtros de permissão.
    Apenas gerentes e administradores podem acessar.
    """
    
    # Obter apenas usuários que o usuário atual pode gerenciar
    users = get_manageable_users_queryset(request.user).select_related('profile').prefetch_related('groups', 'user_permissions')
    
    # Filtros
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    group_filter = request.GET.get('group', '')
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    elif status == 'staff':
        users = users.filter(is_staff=True)
    elif status == 'superuser':
        users = users.filter(is_superuser=True)
    
    if group_filter:
        users = users.filter(groups__id=group_filter)
    
    # Ordenação
    order_by = request.GET.get('order_by', '-date_joined')
    users = users.order_by(order_by)
    
    # Paginação
    paginator = Paginator(users, 25)  # 25 usuários por página
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    # Grupos disponíveis para o usuário atual (apenas os que pode atribuir)
    available_groups = get_allowed_groups_for_user(request.user)
    
    # Estatísticas baseadas nos usuários visíveis
    manageable_users = get_manageable_users_queryset(request.user)
    
    context = {
        'users': users_page,
        'groups': available_groups,
        'search': search,
        'status': status,
        'group_filter': group_filter,
        'order_by': order_by,
        'current_user_level': get_user_level_display(request.user),
        'total_users': manageable_users.count(),
        'active_users': manageable_users.filter(is_active=True).count(),
        'inactive_users': manageable_users.filter(is_active=False).count(),
        'staff_users': manageable_users.filter(is_staff=True).count(),
    }
    
    return render(request, 'user_management/user_list.html', context)


@login_required
@user_management_required
def user_create(request):
    """
    Criar novo usuário.
    Aplica validações de permissão para garantir que apenas grupos permitidos sejam atribuídos.
    """
    
    if request.method == 'POST':
        form = UserManagementForm(
            request.POST, 
            is_editing=False, 
            current_user=request.user
        )
        if form.is_valid():
            # Validação adicional de permissões
            is_valid, errors = validate_user_form_submission(
                request.user, 
                None,  # Novo usuário 
                form.cleaned_data
            )
            
            if not is_valid:
                for error in errors:
                    form.add_error(None, error)
            else:
                # Validar grupos especificamente
                selected_groups = form.cleaned_data.get('groups', [])
                groups_valid, group_error = validate_group_assignment(request.user, selected_groups)
                
                if not groups_valid:
                    form.add_error('groups', group_error)
                else:
                    user = form.save()
                    messages.success(request, f'Usuário {user.username} criado com sucesso!')
                    return redirect('user_management:user_detail', pk=user.pk)
    else:
        form = UserManagementForm(is_editing=False, current_user=request.user)
    
    context = {
        'form': form,
        'title': 'Criar Novo Usuário',
        'button_text': 'Criar Usuário',
        'current_user_level': get_user_level_display(request.user)
    }
    
    return render(request, 'user_management/user_form.html', context)


@login_required
@user_management_required
def user_edit(request, pk):
    """
    Editar usuário existente.
    Aplica todas as regras de permissão e protege o admin principal.
    """
    
    user = get_object_or_404(User, pk=pk)
    
    # Verificar se o usuário atual pode editar este usuário
    if not can_edit_user(request.user, user):
        messages.error(request, 'Você não tem permissão para editar este usuário.')
        return redirect('user_management:user_list')
    
    # Verificar se é usuário protegido (admin principal)
    is_protected_admin = is_protected_user(user)
    
    if request.method == 'POST':
        form = UserManagementForm(
            request.POST, 
            instance=user, 
            is_editing=True, 
            is_protected_admin=is_protected_admin,
            current_user=request.user
        )
        
        if form.is_valid():
            # Validação adicional de permissões
            is_valid, errors = validate_user_form_submission(
                request.user, 
                user, 
                form.cleaned_data
            )
            
            if not is_valid:
                for error in errors:
                    form.add_error(None, error)
            else:
                # Validar grupos especificamente
                selected_groups = form.cleaned_data.get('groups', [])
                groups_valid, group_error = validate_group_assignment(request.user, selected_groups)
                
                if not groups_valid:
                    form.add_error('groups', group_error)
                else:
                    # Proteção adicional para admin principal
                    if is_protected_admin:
                        if not form.cleaned_data.get('is_superuser', True):
                            form.add_error('is_superuser', 'O administrador principal deve manter o status de superusuário.')
                        if not form.cleaned_data.get('is_active', True):
                            form.add_error('is_active', 'O administrador principal deve permanecer ativo.')
                    
                    # Se não há erros, salvar
                    if not form.errors:
                        saved_user = form.save()
                        messages.success(request, f'Usuário {saved_user.username} atualizado com sucesso!')
                        return redirect('user_management:user_detail', pk=saved_user.pk)
    else:
        form = UserManagementForm(
            instance=user, 
            is_editing=True, 
            is_protected_admin=is_protected_admin,
            current_user=request.user
        )
    
    context = {
        'form': form,
        'user_obj': user,
        'title': f'Editar Usuário: {user.username}',
        'button_text': 'Salvar Alterações',
        'is_protected_admin': is_protected_admin,
        'current_user_level': get_user_level_display(request.user),
        'target_user_level': get_user_level_display(user)
    }
    
    return render(request, 'user_management/user_form.html', context)


@login_required
@user_management_required
def user_detail(request, pk):
    """
    Visualizar detalhes do usuário.
    Verifica se o usuário atual pode visualizar o usuário alvo.
    """
    
    user = get_object_or_404(User, pk=pk)
    
    # Verificar se pode visualizar este usuário
    if not can_view_user(request.user, user):
        messages.error(request, 'Você não tem permissão para visualizar este usuário.')
        return redirect('user_management:user_list')
    
    # Permissões do usuário (diretas + de grupos)
    user_permissions = user.get_all_permissions()
    
    # Verificar ações que o usuário atual pode realizar neste usuário
    can_edit = can_edit_user(request.user, user)
    is_protected = is_protected_user(user)
    
    context = {
        'user_obj': user,
        'user_permissions': sorted(user_permissions),
        'groups': user.groups.all(),
        'direct_permissions': user.user_permissions.all(),
        'user_level': get_user_level_display(user),
        'current_user_level': get_user_level_display(request.user),
        'can_edit': can_edit,
        'is_protected': is_protected,
    }
    
    return render(request, 'user_management/user_detail.html', context)


@login_required
@user_management_required
@require_http_methods(["POST"])
def user_toggle_active(request, pk):
    """
    Ativar/Inativar usuário via AJAX.
    Aplica todas as regras de permissão e proteção.
    """
    
    user = get_object_or_404(User, pk=pk)
    
    # Verificar se pode editar este usuário
    if not can_edit_user(request.user, user):
        return JsonResponse({
            'success': False,
            'message': 'Você não tem permissão para alterar este usuário.'
        })
    
    # Admin principal (ID=1) nunca pode ser inativado
    if is_protected_user(user):
        return JsonResponse({
            'success': False,
            'message': 'O administrador principal não pode ser inativado por segurança.'
        })
    
    # Não permitir inativar o próprio usuário
    if user == request.user:
        return JsonResponse({
            'success': False,
            'message': 'Você não pode inativar sua própria conta.'
        })
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'ativado' if user.is_active else 'inativado'
    
    return JsonResponse({
        'success': True,
        'message': f'Usuário {user.username} {status} com sucesso.',
        'is_active': user.is_active
    })


@login_required

@login_required
@user_management_required
def permissions_manage(request, pk):
    """
    Gerenciar permissões de um usuário específico.
    Apenas admin principal pode usar esta interface avançada.
    """
    
    user = get_object_or_404(User, pk=pk)
    
    # Verificar se pode editar este usuário
    if not can_edit_user(request.user, user):
        messages.error(request, 'Você não tem permissão para alterar as permissões deste usuário.')
        return redirect('user_management:user_detail', pk=pk)
    
    # Apenas admin principal pode usar a interface avançada de permissões
    if get_user_level(request.user) != 'admin_principal':
        messages.error(request, 'Apenas o administrador principal pode usar a interface avançada de permissões.')
        return redirect('user_management:user_detail', pk=pk)
    
    if request.method == 'POST':
        # Processar permissões
        selected_permissions = request.POST.getlist('permissions')
        selected_groups = request.POST.getlist('groups')
        
        # Validar grupos
        if selected_groups:
            groups = Group.objects.filter(id__in=selected_groups)
            groups_valid, group_error = validate_group_assignment(request.user, groups)
            if not groups_valid:
                messages.error(request, group_error)
                return redirect('user_management:permissions_manage', pk=pk)
            
            # Atualizar grupos
            user.groups.set(selected_groups)
        
        # Atualizar permissões individuais
        user.user_permissions.set(selected_permissions)
        
        messages.success(request, f'Permissões do usuário {user.username} atualizadas com sucesso!')
        return redirect('user_management:user_detail', pk=pk)
    
    # Organizar permissões por app
    permissions_by_app = {}
    for permission in Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename'):
        app_label = permission.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(permission)
    
    # Grupos disponíveis para o usuário atual
    available_groups = get_allowed_groups_for_user(request.user)
    
    context = {
        'user_obj': user,
        'permissions_by_app': permissions_by_app,
        'all_groups': available_groups,
        'user_permissions': user.user_permissions.all(),
        'user_groups': user.groups.all(),
        'current_user_level': get_user_level_display(request.user),
    }
    
    return render(request, 'user_management/permissions_manage.html', context)


@login_required
@user_management_required
def user_change_password(request, pk):
    """
    Alterar senha de um usuário específico.
    Aplica todas as regras de permissão.
    """
    
    user_obj = get_object_or_404(User, pk=pk)
    
    # Verificar se pode alterar a senha deste usuário
    if not can_edit_user(request.user, user_obj):
        messages.error(request, 'Você não tem permissão para alterar a senha deste usuário.')
        return redirect('user_management:user_detail', pk=pk)
    
    # Não permitir alterar senha do próprio usuário por esta interface
    if user_obj == request.user:
        messages.error(request, 'Para alterar sua própria senha, use o perfil do usuário.')
        return redirect('user_management:user_detail', pk=pk)
    
    # Admin principal protegido
    if is_protected_user(user_obj):
        if get_user_level(request.user) != 'admin_principal':
            messages.error(request, 'Apenas o administrador principal pode alterar sua própria senha por esta interface.')
            return redirect('user_management:user_detail', pk=pk)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not new_password:
            messages.error(request, 'A nova senha é obrigatória.')
        elif len(new_password) < 8:
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
        elif new_password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
        else:
            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, f'Senha do usuário {user_obj.username} alterada com sucesso!')
            return redirect('user_management:user_detail', pk=pk)
    
    context = {
        'user_obj': user_obj,
        'title': f'Alterar Senha: {user_obj.username}'
    }
    
    return render(request, 'user_management/user_change_password.html', context)
