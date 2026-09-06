import uuid

from django.db import models
from users.models import User # Importa o modelo de usuário customizado
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class Address(models.Model):
    cep = models.CharField(max_length=9, verbose_name="CEP") # Ex: 12345-678
    rua = models.CharField(max_length=255, verbose_name="Rua")
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=100, verbose_name="Estado")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cidade}/{self.estado}"

    def update_coordinates(self):
        """Busca as coordenadas aproximadas da cidade/estado para definir a microrregião."""
        geolocator = Nominatim(user_agent="bovine_management_system")
        try:
            query = f"{self.cidade}, {self.estado}, Brasil"
            location = geolocator.geocode(query, timeout=5)
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
        except (GeocoderTimedOut, GeocoderServiceError):
            pass

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            self.update_coordinates()
        super().save(*args, **kwargs)


class FarmUser(models.Model):
    farm = models.ForeignKey('Farm', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False, verbose_name="É Proprietário")

    class Meta:
        unique_together = ('farm', 'user')
        verbose_name = "Usuário da Fazenda"
        verbose_name_plural = "Usuários da Fazenda"

    def __str__(self):
        return f"{self.user.name} em {self.farm.name}"

class Farm(models.Model):
    identifier = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Identificador da Fazenda"
    )
    name = models.CharField(max_length=255, unique=True, verbose_name="Nome da Fazenda")
    image = models.ImageField(upload_to='farm_images/', blank=True, null=True, verbose_name="Imagem da Fazenda")

    address = models.OneToOneField(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Endereço da Fazenda"
    )

    users = models.ManyToManyField(
        User,
        through='FarmUser',
        related_name='farms',
        blank=True,
        verbose_name="Usuários Associados"
    )

    auto_update_categories = models.BooleanField(
        default=True,
        verbose_name="Atualizar Categorias Zootécnicas Automaticamente",
        help_text="Se ativado, altera automaticamente a categoria do animal (ex: Bezerra -> Novilha -> Vaca) baseado na idade e eventos de parto."
    )
    weaning_age_months = models.PositiveIntegerField(
        default=8,
        verbose_name="Idade Média de Desmame (Meses)",
        help_text="Idade em que bezerras(os) passam para a categoria de Novilha/Garrote."
    )
    mating_age_months = models.PositiveIntegerField(
        default=24,
        verbose_name="Idade de Aptidão Reprodutiva / Adulto (Meses)"
    )

    # farm settings
    notify_calving_days_before = models.PositiveIntegerField(
        default=7,
        verbose_name="Dias de Antecedência para Alerta de Parto"
    )
    notify_heat_days_after_calving = models.PositiveIntegerField(
        default=45,
        verbose_name="Dias Pós-Parto para Alerta de Retorno ao Cio"
    )
    notify_drug_withdrawal_days_before = models.PositiveIntegerField(
        default=2,
        verbose_name="Dias de Antecedência para Fim da Carência de Medicamentos"
    )

    class Meta:
        verbose_name = "Fazenda"
        verbose_name_plural = "Fazendas"

    def __str__(self):
        return self.name