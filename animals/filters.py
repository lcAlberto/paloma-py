import django_filters
from .models import Animal

class AnimalFilter(django_filters.FilterSet):
    identifier = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    breed = django_filters.NumberFilter(field_name='breed__id')
    classification = django_filters.NumberFilter(field_name='classification__id')
    status = django_filters.NumberFilter(field_name='status__id')
    farm = django_filters.NumberFilter(field_name='farm__id')

    sex = django_filters.ChoiceFilter(choices=Animal.SEX_CHOICES)
    born_date = django_filters.DateFilter(field_name='born_date')
    born_date_min = django_filters.DateFilter(field_name='born_date', lookup_expr='gte')
    born_date_max = django_filters.DateFilter(field_name='born_date', lookup_expr='lte')

    class Meta:
        model = Animal
        fields = [
            'identifier', 'name', 'sex', 'born_date',
            'breed', 'classification', 'status', 'farm'
        ]