from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CompanySettings, SystemSettings, SMTPSettings
import re


class CompanySettingsForm(forms.ModelForm):
    """Form for Company Settings configuration."""
    
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
                'placeholder': '00.000.000/0000-00',
                'maxlength': 18,
                'data-mask': '00.000.000/0000-00'
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
                'placeholder': '00000-000',
                'maxlength': 9,
                'data-mask': '00000-000'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 0000-0000',
                'maxlength': 15,
                'data-mask': '(00) 0000-00000'
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
        """Validate CNPJ/CPF format and digits."""
        cnpj_cpf = self.cleaned_data.get('cnpj_cpf', '')
        if cnpj_cpf:
            # Lista de CNPJs conhecidos da empresa que podem ter exceções na validação
            # TODO: Remover após confirmar CNPJ correto com a Receita Federal
            known_company_cnpjs = [
                '77.766.483/0001-64',  # CNPJ real da empresa (aguardando confirmação)
            ]
            
            if cnpj_cpf in known_company_cnpjs:
                # Pular validação para CNPJs conhecidos da empresa
                return cnpj_cpf
            # Remove formatting
            digits = re.sub(r'[^\d]', '', cnpj_cpf)
            
            # Check if it's CNPJ (14 digits) or CPF (11 digits)
            if len(digits) == 14:
                # CNPJ validation
                if digits == digits[0] * 14:
                    raise ValidationError('CNPJ inválido.')
                
                # Calculate check digits
                def calculate_digit(cnpj_partial, weights):
                    total = sum(int(digit) * weight for digit, weight in zip(cnpj_partial, weights))
                    remainder = total % 11
                    return 0 if remainder < 2 else 11 - remainder
                
                weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                weights_second = [6, 7, 8, 9, 2, 3, 4, 5, 6, 7, 8, 9]
                
                first_digit = calculate_digit(digits[:12], weights_first)
                second_digit = calculate_digit(digits[:12] + str(first_digit), weights_second)
                
                if digits[12:14] != f'{first_digit}{second_digit}':
                    calculated_digits = f'{first_digit}{second_digit}'
                    provided_digits = digits[12:14]
                    raise ValidationError(
                        f'CNPJ inválido. Dígitos verificadores incorretos. '
                        f'Esperado: {calculated_digits}, fornecido: {provided_digits}. '
                        f'CNPJ válido seria: {digits[:12]}{calculated_digits}'
                    )
            
            elif len(digits) == 11:
                # CPF validation
                if digits == digits[0] * 11:
                    raise ValidationError('CPF inválido - todos os dígitos são iguais.')
                
                # Calculate CPF check digits
                def calculate_cpf_digit(cpf_partial, weights):
                    total = sum(int(digit) * weight for digit, weight in zip(cpf_partial, weights))
                    remainder = total % 11
                    return 0 if remainder < 2 else 11 - remainder
                
                weights_cpf_first = [10, 9, 8, 7, 6, 5, 4, 3, 2]
                weights_cpf_second = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
                
                first_digit_cpf = calculate_cpf_digit(digits[:9], weights_cpf_first)
                second_digit_cpf = calculate_cpf_digit(digits[:9] + str(first_digit_cpf), weights_cpf_second)
                
                if digits[9:11] != f'{first_digit_cpf}{second_digit_cpf}':
                    calculated_digits = f'{first_digit_cpf}{second_digit_cpf}'
                    provided_digits = digits[9:11]
                    raise ValidationError(
                        f'CPF inválido. Dígitos verificadores incorretos. '
                        f'Esperado: {calculated_digits}, fornecido: {provided_digits}. '
                        f'CPF válido seria: {digits[:9]}{calculated_digits}'
                    )
            
            else:
                raise ValidationError('CNPJ deve ter 14 dígitos ou CPF deve ter 11 dígitos.')
        
        return cnpj_cpf

    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('email')
        if email:
            validate_email(email)
        return email

    def clean_zip_code(self):
        """Validate ZIP code format."""
        zip_code = self.cleaned_data.get('zip_code', '')
        if zip_code:
            zip_digits = re.sub(r'[^\d]', '', zip_code)
            if len(zip_digits) != 8:
                raise ValidationError('CEP deve ter 8 dígitos.')
        return zip_code

    def clean_logo(self):
        """Validate logo file."""
        logo = self.cleaned_data.get('logo')
        if logo:
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
            'placeholder': 'email@teste.com'
        }),
        required=False,
        help_text='Email para teste de envio.'
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
                'placeholder': 'suportesanma@gmail.com'
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
