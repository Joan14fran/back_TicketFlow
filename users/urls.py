from django.urls import path
from .views import RegisterView
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView, CustomAuthTokenView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomAuthTokenView.as_view(), name='login'),
]