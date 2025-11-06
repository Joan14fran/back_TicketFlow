from django.urls import path
from .views import RegisterView
from rest_framework.authtoken.views import obtain_auth_token # Vista de Login de DRF

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
]