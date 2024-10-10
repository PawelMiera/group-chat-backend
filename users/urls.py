from django.urls import path
from rest_framework_simplejwt.views import (TokenRefreshView, TokenObtainPairView)
from . import views

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterLoginView.as_view(), name='auth_register'),
    path('user/', views.UserView.as_view(), name="User"),
]
