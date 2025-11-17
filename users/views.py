from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from .models import CustomUser

# --- Vistas para el Login Personalizado ---
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

# /api/register/
class RegisterView(generics.CreateAPIView):
    """
    Vista de API para registrar un nuevo usuario.
    Es una vista de "Solo Creación" (CreateAPIView).
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    
    permission_classes = [AllowAny]

class CustomAuthTokenView(ObtainAuthToken):
    """
    Vista de login personalizada que devuelve token y datos del usuario (incluyendo el rol).
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.pk,
                'username': user.username,
                'email': user.email,
                'role': user.role 
            }
        })