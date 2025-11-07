from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from .models import Category, Ticket, Comment
from .serializers import CategorySerializer, TicketSerializer, CommentSerializer
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
    Endpoint de API para ver Categorías.
    Comentario: Es de solo lectura (ReadOnly) para todos los usuarios autenticados.
    Un admin/agente debería crearlas desde /admin/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class TicketViewSet(viewsets.ModelViewSet):
    """
    Endpoint de API para Tickets (CRUD).
    Aquí ocurre la magia de los roles.
    """
    serializer_class = TicketSerializer

    def get_queryset(self):
        """
        Sobrescribimos este método para filtrar los tickets
        basado en el rol del usuario.
        """
        user = self.request.user
        
        if user.role == 'agent':
            return Ticket.objects.all().order_by('-updated_at')
        else:
            return Ticket.objects.filter(created_by=user).order_by('-updated_at')

    def get_permissions(self):
        """
        Sobrescribimos para asignar permisos por acción.
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'update_ticket']:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrAgent]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            self.permission_classes = [permissions.IsAuthenticated]
        
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Sobrescribimos para asignar automáticamente
        al usuario logueado como el creador del ticket.
        """
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Sobrescribimos el método update para manejar comentarios opcionales
        cuando se actualiza un ticket.
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
            comment_serializer = CommentSerializer(comment)
            comment_data = comment_serializer.data
        
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
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='update-ticket', 
            permission_classes=[permissions.IsAuthenticated, IsOwnerOrAgent])
    def update_ticket(self, request, pk=None):
        """
        Endpoint personalizado para actualizar ticket con comentario opcional.
        URL: /api/tickets/{id}/update-ticket/
        
        Permite actualizar cualquier campo del ticket y agregar un comentario
        en una sola operación.
        
        Body example:
        {
            "status": "in_progress",
            "assigned_to": 2,
            "priority": "high",
            "comment": "Iniciando trabajo en este ticket. Asignado a mí."
        }
        """
        ticket = self.get_object()
        
        comment_content = request.data.pop('comment', None)
        
        for field, value in request.data.items():
            if hasattr(ticket, field):
                setattr(ticket, field, value)
        
        ticket.save()
        
        comment_data = None
        if comment_content:
            comment = Comment.objects.create(
                ticket=ticket,
                user=request.user,
                content=comment_content
            )
            comment_data = CommentSerializer(comment).data
        
        ticket_data = TicketSerializer(ticket).data
        
        response = {
            'ticket': ticket_data,
            'message': 'Ticket actualizado exitosamente'
        }
        
        if comment_data:
            response['new_comment'] = comment_data
            response['message'] = 'Ticket actualizado y comentario agregado exitosamente'
        
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='add-comment', 
            permission_classes=[permissions.IsAuthenticated, IsOwnerOrAgent])
    def add_comment(self, request, pk=None):
        """
        Endpoint para solo agregar un comentario (sin actualizar el ticket).
        URL: /api/tickets/{id}/add-comment/
        
        Se mantiene por compatibilidad, pero se recomienda usar update-ticket
        cuando se quiera actualizar el ticket Y agregar un comentario.
        """
        ticket = self.get_object() 
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user, ticket=ticket)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)