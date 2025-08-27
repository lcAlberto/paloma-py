from rest_framework import serializers
from .models import Farm, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class FarmSerializer(serializers.ModelSerializer):
    # address = AddressSerializer(required=False)

    class Meta:
        model = Farm
        fields = [
            'id',
            'name',
            'image',
            'address',
            'users'
        ]
        read_only_fields = ['id', 'users']

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            address = Address.objects.create(**address_data)
            farm = Farm.objects.create(address=address, **validated_data)
        else:
            farm = Farm.objects.create(**validated_data)
        return farm

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            address_serializer = self.fields['address']
            address_instance = instance.address
            address_serializer.update(address_instance, address_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
