from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm, ChangePasswordForm


class LoginView(FormView):
    """
    View profissional para login com validação e segurança aprimorada
    """
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm
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
            messages.error(self.request, 'Credenciais inválidas. Tente novamente.')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros abaixo.')
        return super().form_invalid(form)


@login_required
def logout_view(request):
    """
    View para logout com mensagem de confirmação
    """
    user_name = request.user.get_full_name() or request.user.username
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
