from rest_framework import serializers

from animals.models import Animal
from .models import ReproductionCycle


class AnimalSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'name', 'identifier', 'sex']


class ReproductionCycleSerializer(serializers.ModelSerializer):
    heat_start_date = serializers.DateTimeField()
    mating_date = serializers.DateTimeField()
    actual_calving_date = serializers.DateTimeField(allow_null=True, required=False)
    predicted_calving_date = serializers.DateTimeField(read_only=True)
    male_animal_id = serializers.PrimaryKeyRelatedField(
        queryset=Animal.objects.filter(sex='male'),
        source='male_animal',
        allow_null=True,
        required=False,
        write_only=True
    )
    female_animal_id = serializers.PrimaryKeyRelatedField(
        queryset=Animal.objects.filter(sex='female'),
        source='female_animal',
        allow_null=False,
        required=True,
        write_only=True
    )
    calf_born_id = serializers.PrimaryKeyRelatedField(
        queryset=Animal.objects.all(),
        source='calf_born',
        allow_null=True,
        required=False,
        write_only=True
    )

    male_animal = AnimalSimpleSerializer(read_only=True)
    female_animal = AnimalSimpleSerializer(read_only=True)
    calf_born = AnimalSimpleSerializer(read_only=True)

    class Meta:
        model = ReproductionCycle
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, data):
        mating_type = data.get('mating_type')
        male_animal = data.get('male_animal')

        if mating_type == 'natural' and not male_animal:
            raise serializers.ValidationError(
                {"male_animal_id": "O touro pai é obrigatório para cobertura natural."}
            )

        status = data.get('status', self.instance.status if self.instance else 'active')

        if status in ['pending', 'active']:
            actual_calving_date = data.get('actual_calving_date')
            calf_born = data.get('calf_born')

            if actual_calving_date:
                raise serializers.ValidationError(
                    {"actual_calving_date": "A data real do parto deve ser nula para ciclos pendentes/ativos."}
                )
            if calf_born:
                raise serializers.ValidationError(
                    {"calf_born_id": "O bezerro nascido deve ser nulo para ciclos pendentes/ativos."}
                )

        if status == 'calved':
            actual_calving_date = data.get('actual_calving_date',
                                           self.instance.actual_calving_date if self.instance else None)
            calf_born = data.get('calf_born', self.instance.calf_born if self.instance else None)

            if not actual_calving_date:
                raise serializers.ValidationError(
                    {"actual_calving_date": "A data real do parto é obrigatória para status 'calved'."}
                )
            if not calf_born:
                raise serializers.ValidationError(
                    {"calf_born_id": "O bezerro nascido é obrigatório para status 'calved'."}
                )

        return data
