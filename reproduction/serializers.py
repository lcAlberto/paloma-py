from rest_framework import serializers
from .models import ReproductionCycle

class ReproductionCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReproductionCycle
        fields = '__all__'
        read_only_fields = ['id', 'predicted_calving_date']