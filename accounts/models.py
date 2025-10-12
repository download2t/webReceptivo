from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import os


def validate_avatar_size(value):
    """
    Valida o tamanho do arquivo de avatar (máximo 12MB)
    """
    filesize = value.size
    if filesize > 12 * 1024 * 1024:  # 12MB em bytes
        raise ValidationError("O arquivo não pode ser maior que 12MB.")
    return value


def user_avatar_path(instance, filename):
    """
    Gera o caminho para upload da foto do usuário
    """
    ext = filename.split('.')[-1].lower()
    filename = f'user_{instance.user.id}_avatar.{ext}'
    return os.path.join('avatars', filename)


class UserProfile(models.Model):
    """
    Perfil estendido do usuário com informações adicionais
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Informações pessoais
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    celular = models.CharField('Celular', max_length=20, blank=True)
    cpf = models.CharField('CPF', max_length=14, blank=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    
    # Endereço
    endereco = models.CharField('Endereço', max_length=255, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)
    cep = models.CharField('CEP', max_length=10, blank=True)
    
    # Avatar
    avatar = models.ImageField(
        'Foto do Perfil',
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        validators=[validate_avatar_size],
        help_text='Formatos aceitos: JPG, PNG, GIF. Tamanho máximo: 12MB.'
    )
    
    # Configurações
    tema_preferido = models.CharField(
        'Tema Preferido',
        max_length=10,
        choices=[('light', 'Claro'), ('dark', 'Escuro'), ('auto', 'Automático')],
        default='auto'
    )
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'
    
    def __str__(self):
        return f'Perfil de {self.user.get_full_name() or self.user.username}'
    
    @property
    def avatar_url(self):
        """
        Retorna a URL do avatar ou um avatar padrão
        """
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default-avatar.svg'
    
    @property
    def nome_completo(self):
        """
        Retorna o nome completo do usuário
        """
        return self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria automaticamente um perfil quando um usuário é criado
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Salva o perfil quando o usuário é salvo
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
