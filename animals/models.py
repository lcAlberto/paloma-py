from django.db import models

from farm.models import Farm
from users.models import User # Importe o nosso modelo de usuário

class Breed(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Classification(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Animal(models.Model):
    SEX_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
    ]

    identifier = models.CharField(max_length=50, unique=True, verbose_name="Identificador único")
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome do animal")
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    born_date = models.DateField(verbose_name="Data de nascimento")
    image = models.ImageField(upload_to='animals_images/', blank=True, null=True)

    mother = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offspring_mother'
    )
    father = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offspring_father'
    )

    breed = models.ForeignKey(Breed, on_delete=models.PROTECT)
    classification = models.ForeignKey(Classification, on_delete=models.PROTECT)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='animals',
        verbose_name="Fazenda"
    )

    def __str__(self):
        return self.name