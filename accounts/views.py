from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from .models import UserProfile
from .forms import UserProfileForm, ChangePasswordForm, CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
# Import para auditoria
from audit_system.signals import log_custom_action


class LoginView(FormView):
    """
    View profissional para login com validação e segurança aprimorada
    """
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('core:dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        # Redirecionar se já estiver logado
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        remember_me = self.request.POST.get('remember_me')
        
        # Verificar se o usuário existe e está inativo antes de autenticar
        try:
            user_check = User.objects.get(username=username)
            if not user_check.is_active:
                # Adicionar erro ao formulário em vez de mensagem
                form.add_error(None, 'Usuário inativo. Entre em contato com o administrador.')
                return self.form_invalid(form)
        except User.DoesNotExist:
            pass  # Continua para o authenticate que dará a mensagem de credenciais inválidas
        
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            
            # Configurar sessão para durar 4 horas por padrão
            if remember_me:
                self.request.session.set_expiry(60 * 60 * 24 * 7)  # 7 dias se marcar "lembrar-me"
            else:
                self.request.session.set_expiry(60 * 60 * 4)  # 4 horas por padrão
            
            messages.success(
                self.request, 
                f'Bem-vindo ao WebReceptivo, {user.get_full_name() or user.username}!'
            )
            
            # Sempre redirecionar para o dashboard (home)
            return redirect(self.success_url)
        else:
            # Adicionar erro ao formulário
            form.add_error(None, 'Credenciais inválidas. Tente novamente.')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # Não adicionar mensagem duplicada - as mensagens específicas já foram adicionadas
        return super().form_invalid(form)


@login_required
def logout_view(request):
    """
    View para logout com mensagem de confirmação
    """
    user_name = request.user.get_full_name() or request.user.username
    
    # Limpar mensagens pendentes da sessão antes do logout
    storage = messages.get_messages(request)
    for message in storage:
        pass  # Consome as mensagens para limpá-las
    storage.used = True
    
    logout(request)
    messages.success(request, f'Até logo, {user_name}! Você foi desconectado com segurança.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    View para exibir e editar perfil do usuário
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        
        if form.is_valid():
            form.save()
            
            # Log da atualização do perfil
            log_custom_action(
                action_name='profile_update',
                obj=request.user,
                user=request.user,
                request=request,
                extra_data={
                    'updated_fields': list(form.changed_data),
                    'has_avatar': bool(profile.avatar),
                }
            )
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    context = {
        'form': form,
        'profile': profile,
        'user': request.user,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """
    View para alteração de senha
    """
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            
            # Fazer login novamente para manter a sessão
            login(request, request.user)
            
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ChangePasswordForm(request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/change_password.html', context)


@login_required
@require_http_methods(["POST"])
def update_theme_view(request):
    """
    View para atualizar a preferência de tema do usuário
    """
    try:
        data = json.loads(request.body)
        theme = data.get('theme')
        
        # Validar tema
        valid_themes = ['light', 'dark', 'auto']
        if theme not in valid_themes:
            return JsonResponse({'error': 'Tema inválido'}, status=400)
        
        # Atualizar perfil do usuário
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.tema_preferido = theme
        profile.save()
        
        return JsonResponse({
            'success': True,
            'theme': theme,
            'message': f'Tema alterado para {theme}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ========== RECUPERAÇÃO DE SENHA ========== #

class CustomPasswordResetView(PasswordResetView):
    """
    View para solicitar recuperação de senha
    """
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            'Instruções de recuperação de senha foram enviadas para seu e-mail.'
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    View de confirmação de envio do email de recuperação
    """
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    View para redefinir a senha
    """
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            'Sua senha foi redefinida com sucesso! Você já pode fazer login.'
        )
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    View de confirmação final da recuperação
    """
    template_name = 'accounts/password_reset_complete.html'
