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
