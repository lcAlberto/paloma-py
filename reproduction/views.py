from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response  # Importamos Response

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
        return (ReproductionCycle.objects.filter(female_animal__farm__in=user_farms)
        .select_related('female_animal', 'male_animal', 'calf_born'))

    def perform_create(self, serializer):
        # O serializer.validated_data contém os objetos Animal
        female_animal = serializer.validated_data.get('female_animal')
        male_animal = serializer.validated_data.get('male_animal')
        user = self.request.user

        # Validação de permissão para Animal Fêmea
        if female_animal.farm not in user.farms.all():
            raise ValidationError(
                {"female_animal_id": "Você não tem permissão para criar ciclos reprodutivos para este animal."}
            )

        # Validação de permissão para Animal Macho (se fornecido)
        # male_animal pode ser None (Ex: inseminação artificial)
        if male_animal and male_animal.farm not in user.farms.all():
            raise ValidationError(
                {"male_animal_id": "Você não tem permissão para usar este animal macho para ciclos reprodutivos."}
            )

        # Salva o ciclo, o que aciona o método save() no Model e calcula o predicted_calving_date
        serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve o método create para retornar a data prevista do parto na resposta.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Salva o objeto (o método save() do modelo calcula a data prevista)
        self.perform_create(serializer)

        # A data prevista do parto já estará no serializer.data após o save
        predicted_date = serializer.data.get('predicted_calving_date')

        # Cria a resposta personalizada (incluindo todos os dados do ciclo + a mensagem)
        response_data = serializer.data

        if predicted_date:
            # Formato da data no BR
            predicted_date_br = predicted_date  # DRF retorna a data no formato ISO
            response_data['message'] = (
                f"Ciclo reprodutivo criado com sucesso! "
                f"A data prevista do parto é: {predicted_date_br}"
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
