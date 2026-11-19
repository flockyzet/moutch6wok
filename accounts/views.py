import requests
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.common.validators import ValidateAgeForProduct
from accounts.permissions import IsModerator

from .google_auth import exchange_code_for_tokens, get_google_user_info
from .models import CustomUser, Product, RegistrationSource
from .serializers import LoginSerializer, ProductSerializer, RegisterSerializer


class RegisterView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "пользователь успешно зарегистрирован!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            birthdate_val = str(user.birthdate) if user.birthdate else None
            refresh["birthdate"] = birthdate_val
            refresh.access_token["birthdate"] = birthdate_val
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "неверный email или пароль"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["code"],
            properties={
                "code": openapi.Schema(type=openapi.TYPE_STRING, description="Authorization code от Google"),
                "redirect_uri": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Redirect URI (по умолчанию http://127.0.0.1:8000/swagger/)",
                ),
            },
        )
    )
    def post(self, request):
        code = request.data.get("code")
        redirect_uri = request.data.get(
            "redirect_uri",
            "http://127.0.0.1:8000/swagger/",
        )

        if not code:
            return Response(
                {"detail": "Поле 'code' обязательно."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tokens = exchange_code_for_tokens(code=code, redirect_uri=redirect_uri)
            access_token = tokens.get("access_token")
            if not access_token:
                return Response(
                    {"detail": "Не удалось получить access_token от Google."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_info = get_google_user_info(access_token=access_token)
        except requests.RequestException as exc:
            return Response(
                {"detail": "Ошибка при обращении к Google OAuth.", "error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = user_info.get("email")
        if not email:
            return Response(
                {"detail": "Google не вернул email пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "registration_source": RegistrationSource.GOOGLE,
                "is_active": True,
            },
        )

        if not created:
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.is_active = True

        user.last_login = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)
        birthdate_val = str(user.birthdate) if user.birthdate else None
        refresh["birthdate"] = birthdate_val
        refresh.access_token["birthdate"] = birthdate_val

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "created": created,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "registration_source": user.registration_source,
                },
            },
            status=status.HTTP_200_OK,
        )


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsModerator]

    def create(self, request, *args, **kwargs):
        validator = ValidateAgeForProduct()
        validator(request)
        return super().create(request, *args, **kwargs)