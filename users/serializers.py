from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para el registro de usuarios.
    Convierte el JSON de la petición a un objeto CustomUser y viceversa.
    """
    
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        """
        Sobrescribimos el método 'create' para hashear la contraseña
        correctamente antes de guardarla en la base de datos.
        """
        password = validated_data.pop('password')
        
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user