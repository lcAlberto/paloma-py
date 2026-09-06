from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'farm',
            'category',
            'category_display',
            'priority',
            'priority_display',
            'title',
            'message',
            'target_object_type',
            'target_object_id',
            'is_read',
            'read_at',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'farm',
            'category',
            'priority',
            'title',
            'message',
            'target_object_type',
            'target_object_id',
            'read_at',
            'created_at',
        ]


# Resultado esperado no retorno da api:
# {
#   "id": 10,
#   "user": 1,
#   "farm": 2,
#   "category": "reproduction",
#   "category_display": "Reprodução e Partos",
#   "priority": "high",
#   "priority_display": "Alta / Crítica",
#   "title": "Aviso de Parto Próximo: Mimosa",
#   "message": "A fêmea Mimosa (BR-202) está prevista para parir em 12/09/2026.",
#   "target_object_type": "animal",
#   "target_object_id": 45,
#   "is_read": false,
#   "read_at": null,
#   "created_at": "2026-09-06T10:30:00Z"
# }