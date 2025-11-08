from django.db import models
from animals.models import Animal, Breed
from datetime import timedelta
import datetime

class SemenDonor(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome do Doador")
    registration_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Registro/Identificador"
    )
    breed = models.ForeignKey(
        Breed,
        on_delete=models.PROTECT,
        verbose_name="Raça"
    )
    born_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Nascimento do Doador"
    )
    origin_farm_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Fazenda de Origem/Central de Coleta"
    )
    collection_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Coleta do Sêmen"
    )

    class Meta:
        verbose_name = "Doador de Sêmen"
        verbose_name_plural = "Doadores de Sêmen"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.breed.name})"

class ReproductionCycle(models.Model):
    MATING_TYPE_CHOICES = [
        ('natural', 'Natural'),
        ('artificial', 'Artificial Insemination'),
    ]

    CYCLE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('calved', 'Calved'),
        ('failed', 'Failed'),
        ('aborted', 'Aborted'),
        ('pending', 'Pending Confirmation'),
    ]

    female_animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='reproduction_cycles_as_female',
        limit_choices_to={'sex': 'female'},
        verbose_name="Animal Fêmea"
    )

    heat_start_date = models.DateTimeField(verbose_name="Data de Início do Cio")
    mating_date = models.DateTimeField(verbose_name="Data da Cobertura")

    mating_type = models.CharField(
        max_length=15,
        choices=MATING_TYPE_CHOICES,
        verbose_name="Tipo de Cobertura"
    )

    male_animal = models.ForeignKey(
        Animal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reproduction_cycles_as_father',
        limit_choices_to={'sex': 'male'},
        verbose_name="Touro (se monta natural)"
    )

    semen_donor = models.ForeignKey(
        SemenDonor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Doador de Sêmen (se IA)"
    )

    predicted_calving_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data Prevista do Parto"
    )

    actual_calving_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data Real do Parto"
    )

    calf_born = models.ForeignKey(
        Animal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reproduction_cycle_of_origin',
        verbose_name="Bezerro Nascido"
    )

    status = models.CharField(
        max_length=20,
        choices=CYCLE_STATUS_CHOICES,
        default='active',
        verbose_name="Status do Ciclo"
    )

    class Meta:
        verbose_name = "Ciclo Reprodutivo"
        verbose_name_plural = "Ciclos Reprodutivos"
        ordering = ['-mating_date']

    def __str__(self):
        return f"Ciclo de {self.female_animal.name} em {self.mating_date}"

    def save(self, *args, **kwargs):
        if self.mating_date and not self.predicted_calving_date:
            self.predicted_calving_date = self.mating_date + timedelta(days=283)

        super().save(*args, **kwargs)

    def clean(self):
        # Lógica de validação ATUALIZADA para usar male_animal
        if self.mating_type == 'natural' and (self.semen_donor is not None or self.male_animal is None):
            raise models.ValidationError({
                'male_animal': 'O Touro é obrigatório para monta natural.',
                'semen_donor': 'O Doador de Sêmen deve ser nulo para monta natural.'
            })
        if self.mating_type == 'artificial' and (self.male_animal is not None or self.semen_donor is None):
            raise models.ValidationError({
                'male_animal': 'O Touro deve ser nulo para IA.',
                'semen_donor': 'O Doador de Sêmen é obrigatório para IA.'
            })
