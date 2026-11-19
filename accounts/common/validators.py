from datetime import date
from rest_framework import serializers


class ValidateAgeForProduct:
    """
    валидатор для проверки возраста пользователя 18+ 
    на основе birthdate полученного из JWT токена
    """
    def call(self, serializer_instance):
        
        request = serializer_instance.context.get('request')
        
        if not request or not request.auth:
            raise serializers.ValidationError("не удалось определить пользователя из токена.")

        
        token_payload = request.auth
        
      
        birthdate_str = token_payload.get('birthdate') if hasattr(token_payload, 'get') else None
        
        
        if not birthdate_str:
            raise serializers.ValidationError("укажите дату рождения, чтобы создать продукт")

        
        if isinstance(birthdate_str, str):
            birthdate = date.fromisoformat(birthdate_str)
        else:
            birthdate = birthdate_str

        # Считаем возраст
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        
        if age < 18:
            raise serializers.ValidationError("вам должно быть 18 лет, чтобы создать продукт")