from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError # IMPORTAÇÃO CORRETA

from .models import Animal
from .serializers import AnimalSerializer
from users.models import User

class AnimalViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_farms = user.farms.all()
        return Animal.objects.filter(farm__in=user_farms)

    def perform_create(self, serializer):
        farm = serializer.validated_data.get('farm')
        user = self.request.user

        if farm and farm not in user.farms.all():
            raise ValidationError(
                {"farm": "Você não tem permissão para criar animais nesta fazenda."}
            )

        serializer.save()

    def perform_update(self, serializer):
        farm = serializer.validated_data.get('farm')
        user = self.request.user

        if farm and farm not in user.farms.all():
            raise ValidationError(
                {"farm": "Você não tem permissão para mover animais para esta fazenda."}
            )

        serializer.save()