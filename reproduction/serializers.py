from datetime import timedelta
from rest_framework import serializers

from animals.models import Animal, Breed
from .models import ReproductionCycle, SemenDonor
from .utils import get_lunar_phase


class BreedSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ['id', 'name', 'value', 'average_gestation_days']


class SemenDonorSerializer(serializers.ModelSerializer):
    breed = BreedSimpleSerializer(read_only=True)
    breed_id = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(),
        source='breed',
        write_only=True,
        required=True
    )

    class Meta:
        model = SemenDonor
        fields = '__all__'
        read_only_fields = ['id']


class AnimalSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'name', 'identifier', 'sex']


class ReproductionCycleSerializer(serializers.ModelSerializer):
    # Campos Read-Only para exibição (nested objects)
    male_animal = AnimalSimpleSerializer(read_only=True)
    semen_donor = SemenDonorSerializer(read_only=True)
    female_animal = AnimalSimpleSerializer(read_only=True)
    calf_born = AnimalSimpleSerializer(read_only=True)

    # Detalhes calculados da previsão (Previsão Refinada + Fase da Lua + Janela)
    prediction_details = serializers.SerializerMethodField()

    # Campos Write-Only para escrita (IDs)
    male_animal_id = serializers.PrimaryKeyRelatedField(
        queryset=Animal.objects.filter(sex='male'),
        source='male_animal',
        allow_null=True,
        required=False,
        write_only=True
    )
    semen_donor_id = serializers.PrimaryKeyRelatedField(
        queryset=SemenDonor.objects.all(),
        source='semen_donor',
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

    class Meta:
        model = ReproductionCycle
        fields = [
            'id', 'female_animal', 'female_animal_id',
            'heat_start_date', 'mating_date', 'mating_type',
            'male_animal', 'male_animal_id',
            'semen_donor', 'semen_donor_id',
            'predicted_calving_date', 'prediction_details',
            'actual_calving_date', 'calf_born', 'calf_born_id', 'status'
        ]
        read_only_fields = ['id', 'predicted_calving_date', 'prediction_details']

    def get_prediction_details(self, obj):
        """
        Retorna o intervalo de confiança zootécnico e a fase da lua no dia previsto.
        """
        if not obj.predicted_calving_date:
            return None

        base_date = obj.predicted_calving_date

        return {
            "estimated_date": base_date,
            "window_start": base_date - timedelta(days=5),
            "window_end": base_date + timedelta(days=5),
            "lunar_phase_at_estimate": get_lunar_phase(base_date),
            "confidence_window_days": 10
        }

    def validate(self, data):
        mating_type = data.get('mating_type', self.instance.mating_type if self.instance else None)
        male_animal = data.get('male_animal', self.instance.male_animal if self.instance else None)
        semen_donor = data.get('semen_donor', self.instance.semen_donor if self.instance else None)

        if mating_type == 'natural':
            if not male_animal:
                raise serializers.ValidationError(
                    {"male_animal_id": "O touro pai é obrigatório para cobertura natural."})
            if semen_donor:
                raise serializers.ValidationError(
                    {"semen_donor_id": "O Doador de Sêmen deve ser nulo para cobertura natural."})

        elif mating_type == 'artificial':
            if not semen_donor:
                raise serializers.ValidationError(
                    {"semen_donor_id": "O Doador de Sêmen é obrigatório para inseminação artificial."})
            if male_animal:
                raise serializers.ValidationError(
                    {"male_animal_id": "O Touro deve ser nulo para inseminação artificial."})

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

# Retorno para api esperado:
    # {
    #     "id": 1,
    #     "female_animal": {"id": 12, "name": "Mimosa", "identifier": "BOV-012", "sex": "female"},
    #     "heat_start_date": "2026-09-01T08:00:00Z",
    #     "mating_date": "2026-09-01T10:00:00Z",
    #     "mating_type": "artificial",
    #     "predicted_calving_date": "2027-06-08T10:00:00Z",
    #     "prediction_details": {
    #         "estimated_date": "2027-06-08T10:00:00Z",
    #         "window_start": "2027-06-03T10:00:00Z",
    #         "window_end": "2027-06-13T10:00:00Z",
    #         "lunar_phase_at_estimate": "Nova",
    #         "confidence_window_days": 10
    #     },
    #     "status": "active"
    # }
