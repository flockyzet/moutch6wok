from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsModerator(BasePermission):
    """
     кастомный permission для модераторов:
     доступ только для пользователей с is_staff = True.
     разрешены безопасные методы (GET, HEAD, OPTIONS), а также PUT, PATCH и DELETE.
     запрещен метод создания (POST).
    """
    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated or not request.user.is_staff:
            return False
            
        
        if request.method == 'POST':
            return False
            
        
        return True