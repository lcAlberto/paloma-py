from datetime import date

from django.db import models

from farm.models import Farm
# from reproduction.models import SemenDonor
from users.models import User
from dateutil.relativedelta import relativedelta

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
    CATEGORY_CHOICES = [
        # Fêmeas
        ('bezerra', 'Bezerra'),
        ('novilha', 'Novilha (Apta/Anestro)'),
        ('vaca_lactante', 'Vaca Lactante'),
        ('vaca_seca', 'Vaca Seca'),
        ('vaca_descarte', 'Vaca Descarte'),
        # Machos
        ('bezerro', 'Bezerro'),
        ('novilho', 'Novilho / Garrote'),
        ('reprodutor', 'Reprodutor / Touro'),
        ('rufiao', 'Rufião'),
        ('capao', 'Castrado / Boi Gordo'),
    ]

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
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='bezerra',
        verbose_name="Categoria Zootécnica"
    )
    is_pregnant = models.BooleanField(
        default=False,
        verbose_name="Está Gestante?"
    )
    is_castrated = models.BooleanField(
        default=False,
        verbose_name="É Castrado?"
    )
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
    def age_in_months(self) -> int:
        if not self.born_date:
            return 0
        today = date.today()
        delta = relativedelta(today, self.born_date)
        return delta.years * 12 + delta.months

    def update_category_by_age(self):
        """Atualiza a categoria zootécnica baseada na idade e nas configurações da fazenda."""
        if not self.farm.auto_update_categories or not self.born_date:
            return

        months = self.age_in_months
        weaning_age = self.farm.weaning_age_months
        mating_age = self.farm.mating_age_months

        if self.sex == 'female':
            # Fêmea não altera categoria se já for uma vaca adulta em ciclo produtivo
            if self.category in ['vaca_lactante', 'vaca_seca']:
                return

            if months < weaning_age:
                self.category = 'bezerra'
            elif months >= weaning_age:
                self.category = 'novilha'

        elif self.sex == 'male':
            if self.is_castrated:
                self.category = 'capao'
                return

            if self.category == 'rufiao':
                return

            if months < weaning_age:
                self.category = 'bezerro'
            elif weaning_age <= months < mating_age:
                self.category = 'novilho'
            else:
                self.category = 'reprodutor'

    def save(self, *args, **kwargs):
        # Dispara atualização por idade se o recurso da fazenda estiver ativado
        if self.farm_id and self.farm.auto_update_categories:
            self.update_category_by_age()
        super().save(*args, **kwargs)

class Comments(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
