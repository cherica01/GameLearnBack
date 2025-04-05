from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .models import User
from .serializers import UserSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
# Inscription utilisateur
@api_view(["POST"])
@csrf_exempt
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(serializer.validated_data["password"])  # Hash du mot de passe
        user.save()

        return Response({"message": "Inscription réussie"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["POST"])
def user_login(request):
    if request.method == "GET":
        return Response({"error": "Utilisez POST pour vous connecter"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    username = request.data.get("username")
    password = request.data.get("password")

    try:
        user = User.objects.get(username=username)
        if not user.check_password(password):
            user = None
    except User.DoesNotExist:
        user = None

    if user:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Connexion réussie",
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)

    return Response({"error": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED)


# Déconnexion utilisateur
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_logout(request):
    logout(request)
    return Response({"message": "Déconnexion réussie"}, status=status.HTTP_200_OK)

# Récupérer le profil utilisateur connecté
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)
