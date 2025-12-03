from rest_framework import serializers
from .models import User
from .passwords import hash_password
from enums.roles import Role


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = hash_password(password)
        validated_data.setdefault('role', Role.MASON)
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
