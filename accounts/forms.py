from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """
    Formulário para edição das informações pessoais do usuário
    """
    first_name = forms.CharField(
        label='Nome',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome'
        })
    )
    
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu sobrenome'
        })
    )
    
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu e-mail'
        })
    )
    
    data_nascimento = forms.DateField(
        label='Data de Nascimento',
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }, format='%Y-%m-%d')
    )
    
    avatar = forms.ImageField(
        label='Foto do Perfil',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text='Formatos aceitos: JPG, PNG, GIF. Tamanho máximo: 12MB.'
    )

    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'telefone', 'celular', 'cpf',
            'endereco', 'cidade', 'estado', 'cep', 'tema_preferido'
        ]
        
        widgets = {
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 3333-4444',
                'data-mask': '(00) 0000-0000'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-8888',
                'data-mask': '(00) 00000-0000'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'data-mask': '000.000.000-00'
            }),

            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua, Número, Complemento'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da cidade'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', 'Selecione o estado'),
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
                ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
                ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
                ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
                ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
            ]),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'data-mask': '00000-000'
            }),

            'tema_preferido': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name  
            self.fields['email'].initial = user.email
            
            # Inicializar data de nascimento se existir no perfil
            if hasattr(user, 'profile') and user.profile.data_nascimento:
                self.fields['data_nascimento'].initial = user.profile.data_nascimento
    
    def clean_avatar(self):
        """
        Validação personalizada para o campo avatar
        """
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Validar extensão
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = avatar.name.lower().split('.')[-1]
            if f'.{ext}' not in valid_extensions:
                raise forms.ValidationError(
                    'Formato de arquivo não suportado. Use JPG, PNG ou GIF.'
                )
            
            # Validar tamanho (12MB)
            if avatar.size > 12 * 1024 * 1024:
                raise forms.ValidationError(
                    'O arquivo é muito grande. Tamanho máximo permitido: 12MB.'
                )
        
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Salvar a data de nascimento
        profile.data_nascimento = self.cleaned_data.get('data_nascimento')
        
        if commit:
            # Salvar dados do usuário
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            
            profile.save()
        
        return profile


class ChangePasswordForm(forms.Form):
    """
    Formulário para alteração de senha
    """
    current_password = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha atual'
        })
    )
    
    new_password = forms.CharField(
        label='Nova Senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha (mínimo 8 caracteres)'
        })
    )
    
    confirm_password = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Senha atual incorreta.')
        return current_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError('As senhas não coincidem.')
        
        return cleaned_data
