from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django import forms
from accounts.models import UserProfile
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
        
        # Para edição, definir valores iniciais antes do super() para CheckboxSelectMultiple
        if self.is_editing and 'instance' in kwargs and kwargs['instance'].pk:
            instance = kwargs['instance']
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            # Usar IDs dos grupos e permissões para o widget CheckboxSelectMultiple
            kwargs['initial']['groups'] = list(instance.groups.values_list('pk', flat=True))
            kwargs['initial']['user_permissions'] = list(instance.user_permissions.values_list('pk', flat=True))
        
        super().__init__(*args, **kwargs)
        
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


@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_list(request):
    """Lista todos os usuários com filtros e paginação"""
    
    users = User.objects.select_related('profile').prefetch_related('groups', 'user_permissions')
    
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
    
    # Grupos para filtro
    groups = Group.objects.all()
    
    context = {
        'users': users_page,
        'groups': groups,
        'search': search,
        'status': status,
        'group_filter': group_filter,
        'order_by': order_by,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
    }
    
    return render(request, 'user_management/user_list.html', context)


@login_required
@permission_required('auth.add_user', raise_exception=True)
def user_create(request):
    """Criar novo usuário"""
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST, is_editing=False)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuário {user.username} criado com sucesso!')
            return redirect('user_management:user_detail', pk=user.pk)
    else:
        form = UserManagementForm(is_editing=False)
    
    context = {
        'form': form,
        'title': 'Criar Novo Usuário',
        'button_text': 'Criar Usuário'
    }
    
    return render(request, 'user_management/user_form.html', context)


@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_edit(request, pk):
    """Editar usuário existente"""
    
    user = get_object_or_404(User, pk=pk)
    
    # Proteção especial para admin principal - não pode remover status de superusuário
    is_protected_admin = (user.id == 1 or user.username == 'admin') and user.is_superuser
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user, is_editing=True, is_protected_admin=is_protected_admin)
        if form.is_valid():
            # Validação adicional para admin principal
            if is_protected_admin:
                # Garantir que campos críticos não sejam alterados
                if not form.cleaned_data.get('is_superuser'):
                    messages.error(request, 'O usuário administrador principal deve manter o status de superusuário.')
                    return render(request, 'user_management/user_form.html', {
                        'form': form, 'user_obj': user, 'title': f'Editar Usuário: {user.username}',
                        'button_text': 'Salvar Alterações', 'is_protected_admin': is_protected_admin
                    })
                if not form.cleaned_data.get('is_active'):
                    messages.error(request, 'O usuário administrador principal deve permanecer ativo.')
                    return render(request, 'user_management/user_form.html', {
                        'form': form, 'user_obj': user, 'title': f'Editar Usuário: {user.username}',
                        'button_text': 'Salvar Alterações', 'is_protected_admin': is_protected_admin
                    })
            
            user = form.save()
            messages.success(request, f'Usuário {user.username} atualizado com sucesso!')
            return redirect('user_management:user_detail', pk=user.pk)
    else:
        form = UserManagementForm(instance=user, is_editing=True, is_protected_admin=is_protected_admin)
    
    context = {
        'form': form,
        'user_obj': user,
        'title': f'Editar Usuário: {user.username}',
        'button_text': 'Salvar Alterações',
        'is_protected_admin': is_protected_admin
    }
    
    return render(request, 'user_management/user_form.html', context)


@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_detail(request, pk):
    """Visualizar detalhes do usuário"""
    
    user = get_object_or_404(User, pk=pk)
    
    # Permissões do usuário (diretas + de grupos)
    user_permissions = user.get_all_permissions()
    
    # Histórico de login (se implementado)
    # login_history = user.login_history.all()[:10]  # Últimos 10 logins
    
    context = {
        'user_obj': user,
        'user_permissions': sorted(user_permissions),
        'groups': user.groups.all(),
        'direct_permissions': user.user_permissions.all(),
        # 'login_history': login_history,
    }
    
    return render(request, 'user_management/user_detail.html', context)


@login_required
@permission_required('auth.change_user', raise_exception=True)
@require_http_methods(["POST"])
def user_toggle_active(request, pk):
    """Ativar/Inativar usuário via AJAX"""
    
    user = get_object_or_404(User, pk=pk)
    
    # Não permitir inativar o próprio usuário
    if user == request.user:
        return JsonResponse({
            'success': False,
            'message': 'Você não pode inativar sua própria conta.'
        })
    
    # Proteger usuário admin principal (ID 1 ou username 'admin')
    if (user.id == 1 or user.username == 'admin') and user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'O usuário administrador principal não pode ser inativado por segurança.'
        })
    
    # Não permitir inativar superusuário (proteção extra)
    if user.is_superuser and not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'Apenas superusuários podem alterar outros superusuários.'
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
@permission_required('auth.delete_user', raise_exception=True)
def user_delete(request, pk):
    """Deletar usuário (com confirmação)"""
    
    user = get_object_or_404(User, pk=pk)
    
    # Não permitir deletar o próprio usuário
    if user == request.user:
        messages.error(request, 'Você não pode deletar sua própria conta.')
        return redirect('user_management:user_detail', pk=pk)
    
    # Proteger usuário admin principal (ID 1 ou username 'admin')
    if (user.id == 1 or user.username == 'admin') and user.is_superuser:
        messages.error(request, 'O usuário administrador principal não pode ser deletado por segurança.')
        return redirect('user_management:user_detail', pk=pk)
    
    # Não permitir deletar superusuário
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Apenas superusuários podem deletar outros superusuários.')
        return redirect('user_management:user_detail', pk=pk)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuário {username} deletado com sucesso.')
        return redirect('user_management:user_list')
    
    context = {
        'user_obj': user,
        'title': f'Deletar Usuário: {user.username}'
    }
    
    return render(request, 'user_management/user_delete.html', context)


@login_required
@permission_required('auth.change_user', raise_exception=True)
def permissions_manage(request, pk):
    """Gerenciar permissões de um usuário específico"""
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Processar permissões
        selected_permissions = request.POST.getlist('permissions')
        selected_groups = request.POST.getlist('groups')
        
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
    
    context = {
        'user_obj': user,
        'permissions_by_app': permissions_by_app,
        'all_groups': Group.objects.all(),
        'user_permissions': user.user_permissions.all(),
        'user_groups': user.groups.all(),
    }
    
    return render(request, 'user_management/permissions_manage.html', context)


@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_change_password(request, pk):
    """Alterar senha de um usuário específico"""
    
    user_obj = get_object_or_404(User, pk=pk)
    
    # Não permitir alterar senha do próprio usuário por esta interface
    if user_obj == request.user:
        messages.error(request, 'Para alterar sua própria senha, use o perfil do usuário.')
        return redirect('user_management:user_detail', pk=pk)
    
    # Proteger usuário admin principal
    if (user_obj.id == 1 or user_obj.username == 'admin') and user_obj.is_superuser:
        if not request.user.is_superuser:
            messages.error(request, 'Apenas superusuários podem alterar a senha do administrador principal.')
            return redirect('user_management:user_detail', pk=pk)
    
    # Verificar se pode alterar senha de superusuário
    if user_obj.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Apenas superusuários podem alterar senhas de outros superusuários.')
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
