from django.db import models
from users.models import User # Importa o modelo de usuário customizado

class Address(models.Model):
    cep = models.CharField(max_length=9, verbose_name="CEP") # Ex: 12345-678
    rua = models.CharField(max_length=255, verbose_name="Rua")
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=100, verbose_name="Estado")

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cidade}/{self.estado}"

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
    identifier = models.CharField(max_length=50, unique=True, verbose_name="Identificador da Fazenda")
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

    class Meta:
        verbose_name = "Fazenda"
        verbose_name_plural = "Fazendas"

    def __str__(self):
        return self.name