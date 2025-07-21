from rest_framework import serializers
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password']
        extra_kwargs = {
            'name': {'required': True},
            'username': {'required': True, 'max_length': 150, 'min_length': 3},
            'email': {'required': True},
            'password': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user