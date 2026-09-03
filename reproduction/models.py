from django.db import models
from animals.models import Animal, Breed
from datetime import timedelta
import datetime
from django.core.exceptions import ValidationError

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

    def calculate_estimated_gestation_days(self) -> int:
        """
        Calcula os dias de gestação ajustados considerando:
        - Raça da fêmea
        - Paridade (se novilha/primípara)
        - Estação do ano / estresse térmico no mês previsto de parto
        """
        # 1. Duração base vinda do modelo Breed
        gestation_days = self.female_animal.breed.average_gestation_days

        # 2. Paridade: Verifica partos anteriores concluídos com sucesso ('calved')
        previous_calvings = ReproductionCycle.objects.filter(
            female_animal=self.female_animal,
            status='calved'
        ).exclude(id=self.id).count()

        if previous_calvings == 0:
            # Primíparas (novilhas) tendem a parir ~2 dias antes
            gestation_days -= 2

        # 3. Estimativa inicial do mês de parto para verificar estação/calor
        tentative_date = self.mating_date + timedelta(days=gestation_days)

        # Se a fazenda tiver latitude definida (Hemisfério Sul) e o parto cair no pico do verão (Dez, Jan, Fev)
        farm_address = getattr(self.female_animal.farm, 'address', None)
        if farm_address and farm_address.latitude:
            # Se for Hemisfério Sul (latitude < 0) e cair em Dezembro, Janeiro ou Fevereiro
            if farm_address.latitude < 0 and tentative_date.month in [12, 1, 2]:
                gestation_days -= 1  # Ligeira antecipação por estresse térmico em épocas quentes

        return gestation_days

    def save(self, *args, **kwargs):
        # Recalcula a previsão se houver mating_date e se for um novo registro ou se predicted_calving_date for nulo
        if self.mating_date and not self.predicted_calving_date:
            gestation_days = self.calculate_estimated_gestation_days()
            self.predicted_calving_date = self.mating_date + timedelta(days=gestation_days)

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.mating_type == 'natural' and not self.male_animal:
            raise ValidationError({'male_animal': 'Touro é obrigatório para cobertura natural.'})

        if self.mating_type == 'artificial' and not self.semen_donor:
            raise ValidationError({'semen_donor': 'Doador de sêmen é obrigatório para inseminação artificial.'})

    # def clean(self):
    #     if self.mating_type == 'natural' and (self.semen_donor is not None or self.male_animal is None):
    #         raise ValidationError({
    #             'male_animal': 'O Touro é obrigatório para monta natural.',
    #             'semen_donor': 'O Doador de Sêmen deve ser nulo para monta natural.'
    #         })
    #     if self.mating_type == 'artificial' and (self.male_animal is not None or self.semen_donor is None):
    #         raise ValidationError({
    #             'male_animal': 'O Touro deve ser nulo para IA.',
    #             'semen_donor': 'O Doador de Sêmen é obrigatório para IA.'
    #         })
