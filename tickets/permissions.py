from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAgent(BasePermission):
    """
    Permiso para verificar si el usuario tiene el rol de 'agent'.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'agent'

class IsOwnerOrAgent(BasePermission):
    """
    Permiso para verificar si el usuario es el dueño del ticket O un agente.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'agent':
            return True
        
        return obj.created_by == request.user