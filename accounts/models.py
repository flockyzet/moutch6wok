from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError


class RegistrationSource(models.TextChoices):
    LOCAL = 'local', 'Local'
    GOOGLE = 'google', 'Google'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('электронная почта должна быть указана')
        email = self.normalize_email(email)
        extra_fields.setdefault('registration_source', RegistrationSource.LOCAL)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('registration_source', RegistrationSource.LOCAL)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('суперпользователь должен иметь is_superuser=True')

        if not extra_fields.get('phone_number'):
            raise ValueError('суперпользователь должен иметь номер телефона')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='электронная почта')
    first_name = models.CharField(max_length=150, blank=True, verbose_name='имя')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='фамилия')
    birthdate = models.DateField(blank=True, null=True, verbose_name='дата рождения')
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='номер телефона'
    )
    registration_source = models.CharField(
        max_length=20,
        choices=RegistrationSource.choices,
        default=RegistrationSource.LOCAL,
        verbose_name='источник регистрации'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def clean(self):
        super().clean()
        if self.phone_number:
            clean_phone = str(self.phone_number).strip().replace('+', '')
            if not clean_phone.startswith('996'):
                raise ValidationError({'phone_number': 'номер телефона должен начинаться с кода 996'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def str(self):
        return self.email


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='название продукта')
    description = models.TextField(verbose_name='описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    def str(self):
        return self.title