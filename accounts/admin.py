
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'phone_number', 'is_staff', 'is_superuser')
    search_fields = ('email', 'phone_number')
    ordering = ('email',)
    
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('персональная информация', {'fields': ('phone_number',)}),
        ('права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2', 'is_staff', 'is_superuser')}
        ),
    )
# Register your models here.
