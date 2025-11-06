from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from .models import CustomUser

# /api/register/
class RegisterView(generics.CreateAPIView):
    """
    Vista de API para registrar un nuevo usuario.
    Es una vista de "Solo Creación" (CreateAPIView).
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    
    permission_classes = [AllowAny]