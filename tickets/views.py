from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from .models import Category, Ticket, Comment
# Importamos los serializers que sí usamos
from .serializers import CategorySerializer, TicketSerializer, CommentSerializer, TicketListSerializer
from .permissions import IsAgent, IsOwnerOrAgent

class HealthCheckView(APIView):
    """
    Vista simple para comprobar que la API está
    funcionando y conectada.
    """
    def get(self, request, *args, **kwargs):
        return Response(
            {"status": "ok", "message": "Backend TicketFlow funcionando!"},
            status=status.HTTP_200_OK
        )

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de API para ver Categorías (solo lectura).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class TicketViewSet(viewsets.ModelViewSet):
    """
    Endpoint de API para Tickets (CRUD).
    """

    def get_queryset(self):
        """
        Filtra los tickets basado en el rol del usuario.
        """
        user = self.request.user
        
        if user.role == 'agent':
            return Ticket.objects.all().order_by('-updated_at')
        else:
            return Ticket.objects.filter(created_by=user).order_by('-updated_at')

    def get_serializer_class(self):
        """
        **MEJORA OPCIONAL**:
        Usamos un serializador ligero para la 'list' 
        y uno completo para 'retrieve' (ver detalles).
        """
        if self.action == 'list':
            return TicketListSerializer
        return TicketSerializer

    def get_permissions(self):
        """
        Asigna permisos por acción.
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'add_comment']:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrAgent]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            self.permission_classes = [permissions.IsAuthenticated]
        
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Asigna automáticamente al usuario logueado como
        el creador del ticket.
        """
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Sobrescribimos el método update (PUT)
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        comment_content = request.data.pop('comment', None)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        comment_data = None
        if comment_content:
            comment = Comment.objects.create(
                ticket=instance,
                user=request.user,
                content=comment_content
            )
            comment_data = CommentSerializer(comment).data
        
        response_data = serializer.data
        if comment_data:
            response_data['new_comment'] = comment_data
            response_data['message'] = 'Ticket actualizado y comentario agregado exitosamente'
        else:
            response_data['message'] = 'Ticket actualizado exitosamente'
        
        return Response(response_data)

    def partial_update(self, request, *args, **kwargs):
        """
        Sobrescribimos partial_update (PATCH) para manejar comentarios opcionales.
        Este es tu método RECOMENDADO.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


    @action(detail=True, methods=['post'], url_path='add-comment', 
            permission_classes=[permissions.IsAuthenticated, IsOwnerOrAgent])
    def add_comment(self, request, pk=None):
        """
        Endpoint para solo agregar un comentario (sin actualizar el ticket).
        URL: POST /api/tickets/tickets/{id}/add-comment/
        """
        ticket = self.get_object() 
        
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user, ticket=ticket)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)