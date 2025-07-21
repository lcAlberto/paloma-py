from rest_framework import serializers
from .models import Animal

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