import django_filters

from reproduction.models import ReproductionCycle


class ReproductionCycleFilter(django_filters.FilterSet):
    # Relacionamentos
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
    semen_donor = django_filters.NumberFilter(
        field_name='semen_donor__id',
        lookup_expr='exact',
        label='ID do Doador de Sêmen'
    )
    farm = django_filters.NumberFilter(
        field_name='female_animal__farm__id',
        lookup_expr='exact',
        label='ID da Fazenda'
    )

    # Enums / Choice fields
    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='exact',
        label='Status do Ciclo (ex: pending, active, calved, cancelled)'
    )
    mating_type = django_filters.CharFilter(
        field_name='mating_type',
        lookup_expr='exact',
        label='Tipo de Cobertura (natural/artificial)'
    )

    # Booleanos
    has_calf = django_filters.BooleanFilter(
        field_name='calf_born',
        lookup_expr='isnull',
        exclude=True,
        label='Com Bezerro Nascido'
    )

    # Intervalos de Datas de Cobertura (mating_date)
    mating_date_after = django_filters.DateFilter(
        field_name='mating_date',
        lookup_expr='gte',
        label='Data de Cobertura - A partir de (AAAA-MM-DD)'
    )
    mating_date_before = django_filters.DateFilter(
        field_name='mating_date',
        lookup_expr='lte',
        label='Data de Cobertura - Até (AAAA-MM-DD)'
    )

    # Intervalos de Datas de Parto Previsto (predicted_calving_date)
    predicted_calving_after = django_filters.DateFilter(
        field_name='predicted_calving_date',
        lookup_expr='gte',
        label='Parto Previsto - A partir de (AAAA-MM-DD)'
    )
    predicted_calving_before = django_filters.DateFilter(
        field_name='predicted_calving_date',
        lookup_expr='lte',
        label='Parto Previsto - Até (AAAA-MM-DD)'
    )

    # Intervalos de Datas de Parto Real (actual_calving_date)
    actual_calving_after = django_filters.DateFilter(
        field_name='actual_calving_date',
        lookup_expr='gte',
        label='Parto Real - A partir de (AAAA-MM-DD)'
    )
    actual_calving_before = django_filters.DateFilter(
        field_name='actual_calving_date',
        lookup_expr='lte',
        label='Parto Real - Até (AAAA-MM-DD)'
    )

    class Meta:
        model = ReproductionCycle
        # Mapeamos apenas o conjunto explícito de filtros para evitar duplicatas e rotas poluídas
        fields = [
            'female_animal',
            'male_animal',
            'semen_donor',
            'farm',
            'status',
            'mating_type',
            'has_calf',
            'mating_date_after',
            'mating_date_before',
            'predicted_calving_after',
            'predicted_calving_before',
            'actual_calving_after',
            'actual_calving_before',
        ]
