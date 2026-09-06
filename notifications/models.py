# notifications/models.py
from django.db import models
from users.models import User
from farm.models import Farm


class Notification(models.Model):
    CATEGORY_CHOICES = [
        ('reproduction', 'Reprodução e Partos'),
        ('clinical', 'Cuidados Clínicos e Medicamentos'),
        ('withdrawal', 'Período de Carência'),
        ('system', 'Avisos do Sistema'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta / Crítica'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Usuário Notificado"
    )
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Fazenda Relacionada"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    title = models.CharField(max_length=255, verbose_name="Título do Alerta")
    message = models.TextField(verbose_name="Conteúdo da Mensagem")

    # Referência opcional para redirecionar no Frontend
    target_object_type = models.CharField(max_length=50, blank=True, null=True,
                                          help_text="Ex: 'animal', 'reproduction_cycle'")
    target_object_id = models.PositiveIntegerField(blank=True, null=True)

    is_read = models.BooleanField(default=False, verbose_name="Lida?")
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title} - {self.user.name}"