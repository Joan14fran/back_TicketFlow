from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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