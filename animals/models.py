from datetime import date

from django.db import models

from farm.models import Farm
# from reproduction.models import SemenDonor
from users.models import User

class Breed(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100, blank=True)
    isEnabled = models.BooleanField(default=True)

    average_gestation_days = models.PositiveSmallIntegerField(
        default=283,
        verbose_name="Dias Médios de Gestação"
    )

    def __str__(self):
        return self.name

class Classification(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100, blank=True)
    isReproducible = models.BooleanField(default=True)
    isEnabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100, blank=True)
    isReproducible = models.BooleanField(default=True)
    isEnabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Animal(models.Model):
    SEX_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
    ]

    DISASSOCIATED_CHOICES = [
        ('sold', 'Sold'),
        ('dead', 'Dead'),
        ('offline', 'Offline'),
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
    semen_donor_father = models.ForeignKey(
        'reproduction.SemenDonor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offspring_donor_father',
        verbose_name="Pai (Doador de Sêmen)"
    )
    breed = models.ForeignKey(Breed, on_delete=models.PROTECT)
    classification = models.ForeignKey(Classification, on_delete=models.PROTECT)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    is_alive = models.BooleanField(default=True)
    dissociated_reasons = models.TextField(
        blank=True,
        null=True,
        max_length=10,
        choices=DISASSOCIATED_CHOICES
    )

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='animals',
        verbose_name="Fazenda"
    )

    def __str__(self):
        return self.name

    def _get_age_in_months(self):
        """Calcula a idade do animal em meses."""
        if not self.born_date:
            return 0
        today = date.today()
        # Calcula a diferença total em meses
        age_months = (today.year - self.born_date.year) * 12 + (today.month - self.born_date.month)

        # Ajusta se o dia de hoje for anterior ao dia de nascimento no mês atual
        if today.day < self.born_date.day:
            age_months -= 1

        return max(0, age_months)

    @property
    def current_life_stage(self):
        """Retorna o estágio de vida do animal com base na idade (calculado)."""
        age_months = self._get_age_in_months()

        if self.sex == 'male':
            if age_months < 6:
                return "Bezerro"
            elif age_months < 24:
                return "Garrote"
            else:
                return "Macho Adulto"  # Classificação de uso (Capão, Touro, Rufião) é manual

        elif self.sex == 'female':
            if age_months < 6:
                return "Bezerra"
            elif age_months < 24:
                return "Novilha"
            else:
                return "Fêmea Adulta"  # Classificação de uso (Leiteira, Seca) é manual

        return "Desconhecido"

class Comments(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
