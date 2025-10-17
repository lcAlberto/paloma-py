from rest_framework import serializers

from animals.models import Animal
from .models import ReproductionCycle


class AnimalSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'name', 'identifier', 'sex']

class ReproductionCycleSerializer(serializers.ModelSerializer):
    male_animal_id = serializers.PrimaryKeyRelatedField(
        queryset=Animal.objects.filter(sex='male'),
        source='male_animal',
        allow_null=False,
        required=True
    )
    female_animal_id = serializers.PrimaryKeyRelatedField(
        queryset=Animal.objects.filter(sex='female'),
        source='female_animal',
        allow_null=False,
        required=True
    )

    male_animal = AnimalSimpleSerializer(read_only=True)
    female_animal = AnimalSimpleSerializer(read_only=True)
    calf_born = AnimalSimpleSerializer(read_only=True)

    class Meta:
        model = ReproductionCycle
        fields = '__all__'
        read_only_fields = ['id', 'predicted_calving_date']