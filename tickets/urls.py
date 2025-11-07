from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthCheckView, CategoryViewSet, TicketViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('', include(router.urls)), 
]