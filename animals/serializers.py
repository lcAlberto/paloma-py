from rest_framework import serializers
from .models import Animal, Breed, Classification, Status
from farm.models import Farm


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ['id', 'name', 'identifier']


class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ['id', 'name', 'value']


class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ['id', 'name', 'value']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'value']


class ParentAnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'name', 'identifier', 'sex']

class AnimalSerializer(serializers.ModelSerializer):
    farm = FarmSerializer(read_only=True)
    breed = BreedSerializer(read_only=True)
    classification = ClassificationSerializer(read_only=True)
    status = StatusSerializer(read_only=True)
    mother = ParentAnimalSerializer(read_only=True)
    father = ParentAnimalSerializer(read_only=True)

    farm_id = serializers.PrimaryKeyRelatedField(
        queryset=Farm.objects.all(), source='farm', write_only=True
    )
    breed_id = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(), source='breed', write_only=True
    )
    classification_id = serializers.PrimaryKeyRelatedField(
        queryset=Classification.objects.all(), source='classification', write_only=True
    )
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), source='status', write_only=True
    )
    mother_id = serializers.PrimaryKeyRelatedField(
        queryset=Animal.objects.filter(sex='female'),
        source='mother',
        allow_null=True,
        required=False,
        write_only=True
    )
    father_id = serializers.PrimaryKeyRelatedField(
        queryset=Animal.objects.filter(sex='male'),
        source='father',
        allow_null=True,
        required=False,
        write_only=True
    )

    class Meta:
        model = Animal

        fields = [
            'id', 'identifier', 'name', 'sex', 'born_date', 'image',
            'farm', 'breed', 'classification', 'status', 'mother', 'father',
            'farm_id', 'breed_id', 'classification_id', 'status_id',
            'mother_id', 'father_id'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        breed_id = data.get('breed')
        classification_id = data.get('classification')
        status_id = data.get('status')
        mother_id = data.get('mother')
        father_id = data.get('father')
        farm_id = data.get('farm')

        if breed_id and not Breed.objects.filter(id=breed_id).exists():
            raise serializers.ValidationError({'breed': 'Raça inválida.'})
        if classification_id and not Classification.objects.filter(id=classification_id).exists():
            raise serializers.ValidationError({'classification': 'Classificação inválida.'})
        if status_id and not Status.objects.filter(id=status_id).exists():
            raise serializers.ValidationError({'status': 'Status inválido.'})
        if mother_id and not Animal.objects.filter(id=mother_id, sex='female').exists():
            raise serializers.ValidationError({'mother': 'Mãe inválida ou não é fêmea.'})
        if father_id and not Animal.objects.filter(id=father_id, sex='male').exists():
            raise serializers.ValidationError({'father': 'Pai inválido ou não é macho.'})
        if farm_id and not Farm.objects.filter(id=farm_id).exists():
            raise serializers.ValidationError({'farm': 'Fazenda inválida.'})
        return data

    def create(self, validated_data):
        return Animal.objects.create(**validated_data)
