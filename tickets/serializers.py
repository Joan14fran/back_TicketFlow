from rest_framework import serializers
from .models import Category, Ticket, Comment
from users.models import CustomUser

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializador simple para Categorías.
    """
    class Meta:
        model = Category
        fields = ('id', 'name')

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializador para Comentarios.
    """
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'user_id', 'user_role', 'content', 'created_at')
        read_only_fields = ('id', 'user', 'user_id', 'user_role', 'created_at')

class TicketSerializer(serializers.ModelSerializer):
    """
    Serializador principal para Tickets.
    Maneja la lógica de lectura y escritura.
    """
    
    created_by = serializers.StringRelatedField(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(source='created_by', read_only=True)
    assigned_to_username = serializers.StringRelatedField(source='assigned_to', read_only=True)
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    
    comments = CommentSerializer(many=True, read_only=True)
    
    comment = serializers.CharField(write_only=True, required=False, allow_blank=True)

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        write_only=True
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role='agent'),
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = Ticket
        fields = (
            'id', 'title', 'description', 'status', 'priority',
            'created_at', 'updated_at',
            'category', 
            'category_name', 
            'created_by', 
            'created_by_id',
            'assigned_to', 
            'assigned_to_username', 
            'comments', 
            'comment'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by_id')

class TicketUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador específico para actualizaciones de tickets con comentario opcional.
    Permite actualizar campos específicos y agregar un comentario en una sola operación.
    """
    comment = serializers.CharField(write_only=True, required=False, allow_blank=True,
                                   help_text="Comentario opcional a agregar al actualizar el ticket")
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role='agent'),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Ticket
        fields = ('status', 'priority', 'assigned_to', 'comment')
        
    def update(self, instance, validated_data):
        """
        Actualiza el ticket y opcionalmente crea un comentario.
        """
        comment_content = validated_data.pop('comment', None)
        
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        
        if comment_content and self.context.get('request'):
            Comment.objects.create(
                ticket=instance,
                user=self.context['request'].user,
                content=comment_content
            )
        
        return instance

class TicketListSerializer(serializers.ModelSerializer):
    """
    Serializador simplificado para listados de tickets (sin comentarios anidados).
    Más eficiente para cuando se listan muchos tickets.
    """
    created_by = serializers.StringRelatedField(read_only=True)
    assigned_to_username = serializers.StringRelatedField(source='assigned_to', read_only=True)
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    
    class Meta:
        model = Ticket
        fields = (
            'id', 'title', 'status', 'priority',
            'category_name', 'created_by', 'assigned_to_username',
            'comments_count', 'created_at', 'updated_at'
        )