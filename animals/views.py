import datetime

from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .filters import AnimalFilter
from .models import Animal, Status, Classification, Breed
from .serializers import AnimalSerializer, BreedSerializer, ClassificationSerializer, StatusSerializer, \
    ParentAnimalSerializer
from django_filters.rest_framework import DjangoFilterBackend
from users.models import User


class AnimalViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_class = AnimalFilter

    def get_queryset(self):
        user = self.request.user
        user_farms = user.farms.all()

        return Animal.objects.filter(farm__in=user_farms).select_related(
            'mother', 'father', 'breed', 'classification', 'status', 'farm'
        )
        # return Animal.objects.filter(farm__in=user_farms)

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


class ParentsListAPIView(generics.ListAPIView):
    serializer_class = ParentAnimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_farms = user.farms.all()

        today = datetime.date.today()
        one_year_ago = today - datetime.timedelta(days=365)

        reproducible_classifications = Classification.objects.filter(isReproducible=True)

        queryset = Animal.objects.filter(
            farm__in=user_farms,
            is_active=True,
            is_alive=True,
            classification__in=reproducible_classifications,
            born_date__lte=one_year_ago
        ).order_by('name')

        # Acessa o parâmetro 'sex' dos query params (?sex=...)
        sex = self.request.query_params.get('sex')
        if sex == 'female':
            return queryset.filter(sex='female')
        elif sex == 'male':
            return queryset.filter(sex='male')
        return queryset.none()

class BreedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [IsAuthenticated]

class ClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Classification.objects.all()
    serializer_class = ClassificationSerializer
    permission_classes = [IsAuthenticated]

class StatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated]