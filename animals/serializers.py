from rest_framework import serializers
from .models import Animal, Breed, Classification, Status
from farm.models import Farm

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = [
            'id',
            'identifier',
            'name',
            'sex',
            'born_date',
            'image',
            'mother',
            'father',
            'breed',
            'classification',
            'status',
            'farm'
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