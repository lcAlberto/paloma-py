from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=150, unique=True, verbose_name="Nome de usuário")
    username = models.CharField(max_length=150, unique=True, blank=True, null=True, verbose_name="Nome de usuário (opcional)")
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name


class UserPreference(models.Model):
    THEME_CHOICES = [
        ('light', 'Claro'),
        ('dark', 'Escuro'),
        ('system', 'Padrão do Sistema'),
    ]

    LANGUAGE_CHOICES = [
        ('pt-br', 'Português (Brasil)'),
        ('en', 'English'),
        ('es', 'Español'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='system')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='pt-br')

    # Canais de notificação preferidos pelo usuário
    notify_by_email = models.BooleanField(default=True, verbose_name="Receber Notificações por E-mail")
    notify_by_push = models.BooleanField(default=True, verbose_name="Receber Push Notifications (Mobile)")
    notify_by_whatsapp = models.BooleanField(default=False, verbose_name="Receber via WhatsApp")

    class Meta:
        verbose_name = "Preferência do Usuário"
        verbose_name_plural = "Preferências dos Usuários"