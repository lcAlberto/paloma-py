from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response  # Importamos Response

from .filters import ReproductionCycleFilter
from .models import ReproductionCycle, SemenDonor
from .serializers import ReproductionCycleSerializer, SemenDonorSerializer


class SemenDonorViewSet(viewsets.ModelViewSet):
    queryset = SemenDonor.objects.all()
    serializer_class = SemenDonorSerializer
    permission_classes = [IsAuthenticated]


class ReproductionCycleViewSet(viewsets.ModelViewSet):
    serializer_class = ReproductionCycleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReproductionCycleFilter

    def get_queryset(self):
        user = self.request.user
        user_farms = user.farms.all()
        return (ReproductionCycle.objects.filter(female_animal__farm__in=user_farms)
        .select_related('female_animal', 'male_animal', 'semen_donor', 'calf_born'))

    def perform_create(self, serializer):
        female_animal = serializer.validated_data.get('female_animal')
        male_animal = serializer.validated_data.get('male_animal')
        user = self.request.user

        if female_animal.farm not in user.farms.all():
            raise ValidationError(
                {"female_animal_id": "Você não tem permissão para criar ciclos reprodutivos para este animal."}
            )

        if male_animal and male_animal.farm not in user.farms.all():
            raise ValidationError(
                {"male_animal_id": "Você não tem permissão para usar este touro para ciclos reprodutivos."}
            )

        serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve o método create para retornar a data prevista do parto na resposta.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        predicted_date = serializer.data.get('predicted_calving_date')

        response_data = serializer.data

        if predicted_date:
            response_data['message'] = (
                f"Ciclo reprodutivo criado com sucesso! "
                f"A data prevista do parto é: {predicted_date}"
            )
        else:
            response_data['message'] = "Ciclo reprodutivo criado com sucesso."

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        female_animal = serializer.validated_data.get('female_animal')
        user = self.request.user

        if female_animal.farm not in user.farms.all():
            raise ValidationError(
                {"female_animal_id": "Você não tem permissão para atualizar ciclos reprodutivos para este animal."}
            )

        serializer.save()
