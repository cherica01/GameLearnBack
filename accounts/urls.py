from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register, user_login, user_logout, user_profile

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("profile/", user_profile, name="user_profile"),
    
    # Rafraîchir le token JWT
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]