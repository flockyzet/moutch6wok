from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema

from .models import Product
from .serializers import RegisterSerializer, LoginSerializer, ProductSerializer
from accounts.permissions import IsModerator
from accounts.common.validators import ValidateAgeForProduct


class RegisterView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "пользователь успешно зарегистрирован!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            birthdate_val = str(user.birthdate) if user.birthdate else None
            refresh['birthdate'] = birthdate_val
            refresh.access_token['birthdate'] = birthdate_val
            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "неверный email или пароль"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsModerator]

    def create(self, request, *args, **kwargs):
        validator = ValidateAgeForProduct()
        validator(request)
        return super().create(request, *args, **kwargs)