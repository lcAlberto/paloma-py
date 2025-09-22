from rest_framework import viewsets, status, generics, serializers
from datetime import date
from .models import Animal, Breed, Classification, Status
from farm.models import Farm
from loguru import logger


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
    age = serializers.SerializerMethodField()

    class Meta:
        model = Animal
        fields = ['id', 'name', 'identifier', 'sex', 'age']

    def get_age(self, obj):
        today = date.today()
        if obj.born_date:
            age_in_days = (today - obj.born_date).days
            return age_in_days // 365
        return None

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
            'mother_id', 'father_id', 'is_active',  'is_alive'
        ]
        read_only_fields = ['id', 'age' ]

    def validate(self, data):
        return data

    def create(self, validated_data):
        return Animal.objects.create(**validated_data)
