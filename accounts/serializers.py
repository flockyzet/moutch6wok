from .models import Product
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=True)  

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'password')

    def validate_phone_number(self, value):
        
        clean_phone = str(value).strip().replace('+', '')
        if not clean_phone.startswith('996'):
            raise serializers.ValidationError("номер телефона должен начинаться с кода 996.")
        return value

    def create(self, validated_data):
        
        user = User.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)





class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['birthdate'] = str (user.birthdate) if user.birthdate else None
        return token