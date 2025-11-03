import django_filters

from reproduction.models import ReproductionCycle


class ReproductionCycleFilter(django_filters.FilterSet):
    female_animal = django_filters.NumberFilter(
        field_name='female_animal__id',
        lookup_expr='exact',
        label='ID da Fêmea (Mãe)'
    )
    male_animal = django_filters.NumberFilter(
        field_name='male_animal__id',
        lookup_expr='exact',
        label='ID do Macho (Pai)'
    )
    mating_date = django_filters.DateRangeFilter(
        field_name='mating_date',
        label='Período da Cobertura (DD/MM/AAAA,DD/MM/AAAA)'
    )
    predicted_calving_date = django_filters.DateRangeFilter(
        field_name='predicted_calving_date',
        label='Período de Parto Previsto (DD/MM/AAAA,DD/MM/AAAA)'
    )
    actual_calving_date = django_filters.DateRangeFilter(
        field_name='actual_calving_date',
        label='Período de Parto Real (DD/MM/AAAA,DD/MM/AAAA)'
    )
    has_calf = django_filters.BooleanFilter(
        field_name='calf_born',
        lookup_expr='isnull',
        exclude=True,
        label='Com Bezerro Nascido'
    )

    # status = django_filters.CharFilter(field_name='status__name', lookup_expr='iexact')
    # start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    # start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    # end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    # end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = ReproductionCycle
        fields = [
            'status',
            'mating_type',
            'female_animal',
            'male_animal',
            'mating_date',
            'predicted_calving_date',
            'actual_calving_date',
            'has_calf',
        ]

    # class Meta:
    #     model = None
    #     fields = ['animal_id', 'status', 'start_date_after', 'start_date_before', 'end_date_after', 'end_date_before']