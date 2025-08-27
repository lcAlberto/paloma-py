from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import ReproductionCycle
from .serializers import ReproductionCycleSerializer

class ReproductionCycleViewSet(viewsets.ModelViewSet):
    serializer_class = ReproductionCycleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Garante que um usuário só possa ver os ciclos reprodutivos
        # de suas próprias fazendas.
        user = self.request.user
        user_farms = user.farms.all()
        # Filtra os ciclos onde a fêmea pertence a uma das fazendas do usuário
        return ReproductionCycle.objects.filter(female_animal__farm__in=user_farms)

    def perform_create(self, serializer):
        # Impede que o usuário crie um ciclo reprodutivo para uma fêmea
        # que não pertence à sua fazenda.
        female_animal = serializer.validated_data.get('female_animal')
        user = self.request.user

        if female_animal.farm not in user.farms.all():
            raise ValidationError(
                {"female_animal": "Você não tem permissão para criar ciclos reprodutivos para este animal."}
            )

        serializer.save()

    def perform_update(self, serializer):
        # Garante que o usuário só possa atualizar ciclos reprodutivos
        # de sua própria fazenda.
        female_animal = serializer.validated_data.get('female_animal')
        user = self.request.user

        if female_animal.farm not in user.farms.all():
            raise ValidationError(
                {"female_animal": "Você não tem permissão para atualizar ciclos reprodutivos para este animal."}
            )

        serializer.save()