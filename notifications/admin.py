# notifications/admin.py
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Campos exibidos na tabela de listagem
    list_display = (
        'id',
        'title',
        'user',
        'farm',
        'category',
        'priority',
        'is_read',
        'created_at',
    )

    # Filtros na lateral direita
    list_filter = (
        'category',
        'priority',
        'is_read',
        'created_at',
        'farm',
    )

    # Campos de busca (barra de pesquisa)
    search_fields = (
        'title',
        'message',
        'user__name',
        'user__email',
        'farm__name',
    )

    # Campos somente leitura (evita edições acidentais no histórico)
    readonly_fields = (
        'created_at',
        'read_at',
    )

    # Ordenação padrão (mais recentes primeiro)
    ordering = ('-created_at',)

    # Melhora a performance de seleção de chaves estrangeiras caso haja muitos usuários/fazendas
    raw_id_fields = ('user', 'farm')