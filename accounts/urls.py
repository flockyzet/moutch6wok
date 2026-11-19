from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, ProductViewSet, GoogleAuthView


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path ('google-auth/', GoogleAuthView.as_view(), name='google-auth'),
    
    path('', include(router.urls)),
]