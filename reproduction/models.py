from django.db import models
from animals.models import Animal
from datetime import timedelta

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
        on_delete=models.PROTECT,
        related_name='reproduction_cycles_as_female',
        limit_choices_to={'sex': 'female'},
        verbose_name="Animal Fêmea"
    )

    heat_start_date = models.DateField(verbose_name="Data de Início do Cio")
    mating_date = models.DateField(verbose_name="Data da Cobertura")

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
        related_name='reproduction_cycles_as_male',
        limit_choices_to={'sex': 'male'},
        verbose_name="Animal Macho (se natural)"
    )

    predicted_calving_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data Prevista do Parto"
    )

    actual_calving_date = models.DateField(
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
        # Calcula a data prevista do parto se a data de cobertura for fornecida
        # Período de gestação médio para gado é de ~283 dias
        if self.mating_date and not self.predicted_calving_date:
            self.predicted_calving_date = self.mating_date + timedelta(days=283)
        super().save(*args, **kwargs)