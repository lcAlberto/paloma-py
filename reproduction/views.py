from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .filters import ReproductionCycleFilter
from .models import ReproductionCycle
from .serializers import ReproductionCycleSerializer

class ReproductionCycleViewSet(viewsets.ModelViewSet):
    serializer_class = ReproductionCycleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReproductionCycleFilter

    def get_queryset(self):
        user = self.request.user
        user_farms = user.farms.all()
        return ReproductionCycle.objects.filter(female_animal__farm__in=user_farms).select_related(
            'female_animal', 'male_animal', 'calf_born')

    def perform_create(self, serializer):
        female_animal = serializer.validated_data.get('female_animal')
        user = self.request.user

        if female_animal.farm not in user.farms.all():
            raise ValidationError(
                {"female_animal": "Você não tem permissão para criar ciclos reprodutivos para este animal."}
            )

        serializer.save()

    def perform_update(self, serializer):
        female_animal = serializer.validated_data.get('female_animal')
        user = self.request.user

        if female_animal.farm not in user.farms.all():
            raise ValidationError(
                {"female_animal": "Você não tem permissão para atualizar ciclos reprodutivos para este animal."}
            )

        serializer.save()