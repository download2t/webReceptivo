from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CompanySettings, SystemSettings, SMTPSettings
import re


class CompanySettingsForm(forms.ModelForm):
    """Form for Company Settings configuration."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classe is-invalid aos campos com erro
        if hasattr(self, 'errors'):
            for field_name, errors in self.errors.items():
                if field_name != '__all__' and field_name in self.fields:
                    field_widget = self.fields[field_name].widget
                    if 'class' in field_widget.attrs:
                        field_widget.attrs['class'] += ' is-invalid'
                    else:
                        field_widget.attrs['class'] = 'is-invalid'
    
    class Meta:
        model = CompanySettings
        fields = [
            'company_name', 'cnpj_cpf', 'state_registration', 'street', 
            'number', 'complement', 'neighborhood', 'city', 'state', 
            'zip_code', 'phone', 'email', 'logo'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da Empresa',
                'maxlength': 200
            }),
            'cnpj_cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CNPJ ou CPF',
                'maxlength': 20
            }),
            'state_registration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Inscrição Estadual',
                'maxlength': 20
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Logradouro',
                'maxlength': 200
            }),
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'maxlength': 10
            }),
            'complement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento',
                'maxlength': 100
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro',
                'maxlength': 100
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'maxlength': 100
            }),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CEP',
                'maxlength': 10
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefone',
                'maxlength': 20
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@empresa.com.br'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            })
        }

    def clean_cnpj_cpf(self):
        """Retorna CNPJ/CPF sem validação de formato."""
        cnpj_cpf = self.cleaned_data.get('cnpj_cpf', '')
        return cnpj_cpf

    def clean_email(self):
        """Retorna email sem validação rigorosa de formato."""
        email = self.cleaned_data.get('email')
        return email

    def clean_zip_code(self):
        """Retorna CEP sem validação de formato."""
        zip_code = self.cleaned_data.get('zip_code', '')
        return zip_code

    def clean_logo(self):
        """Validate logo file."""
        logo = self.cleaned_data.get('logo')
        if logo:
            # Verificar se é um novo upload (tem content_type)
            # Se for ImageFieldFile (arquivo já salvo), não validar
            if hasattr(logo, 'content_type'):
                # Check file size (max 5MB)
                if logo.size > 5 * 1024 * 1024:
                    raise ValidationError('O arquivo da logo deve ter no máximo 5MB.')
                
                # Check file type
                valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if logo.content_type not in valid_types:
                    raise ValidationError('Formato de arquivo não suportado. Use JPEG, PNG, GIF ou WebP.')
        
        return logo


class SystemSettingsForm(forms.ModelForm):
    """Form for System Settings configuration."""
    
    class Meta:
        model = SystemSettings
        fields = ['timezone', 'date_format', 'time_format']
        widgets = {
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'date_format': forms.Select(attrs={'class': 'form-control'}),
            'time_format': forms.Select(attrs={'class': 'form-control'})
        }




class SMTPSettingsForm(forms.ModelForm):
    """Form for SMTP Settings configuration."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha do email'
        }),
        required=False,
        help_text='Deixe em branco para manter a senha atual.'
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        }),
        required=False,
        help_text='Confirme a nova senha.'
    )
    
    test_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@exemplo.com.br'
        }),
        required=False,
        help_text='Email para receber o teste de envio.'
    )
    
    class Meta:
        model = SMTPSettings
        fields = [
            'email_backend', 'smtp_server', 'smtp_port', 'email', 'connection_security', 
            'timeout', 'is_active'
        ]
        widgets = {
            'email_backend': forms.Select(attrs={
                'class': 'form-control',
                'title': 'Backend de e-mail do Django'
            }),
            'smtp_server': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'smtp.gmail.com'
            }),
            'smtp_port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '587',
                'min': 1,
                'max': 65535
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contato@webreceptivo.com.br'
            }),
            'connection_security': forms.Select(attrs={'class': 'form-control'}),
            'timeout': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30',
                'min': 1,
                'max': 300
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'title': 'Ativar estas configurações para o sistema'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password from form if editing existing instance
        if self.instance and self.instance.pk:
            self.fields['password'].help_text = 'Deixe em branco para manter a senha atual.'
            self.fields['confirm_password'].help_text = 'Confirme apenas se alterando a senha.'

    def clean_smtp_server(self):
        """Validate SMTP host."""
        host = self.cleaned_data.get('smtp_server', '').strip()
        if not host:
            raise ValidationError('Servidor SMTP é obrigatório.')
        return host

    def clean_smtp_port(self):
        """Validate SMTP port."""
        port = self.cleaned_data.get('smtp_port')
        if port is None:
            raise ValidationError('Porta SMTP é obrigatória.')
        if port < 1 or port > 65535:
            raise ValidationError('Porta deve estar entre 1 e 65535.')
        return port

    def clean_email(self):
        """Validate SMTP email."""
        email = self.cleaned_data.get('email')
        if email:
            validate_email(email)
        return email

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Password confirmation
        if password and password != confirm_password:
            raise ValidationError('As senhas não coincidem.')

        return cleaned_data

    def save(self, commit=True):
        """Save form with password encryption."""
        instance = super().save(commit=False)
        
        # Only update password if provided
        password = self.cleaned_data.get('password')
        if password:
            instance.smtp_password = password
        
        if commit:
            instance.save()
        
        return instance
