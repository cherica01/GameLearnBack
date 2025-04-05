from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  UserProgressViewSet,TestAuthenticationView
from ai.views import test_chat_service
from ai.views import HistoricalCharacterViewSet
router = DefaultRouter()
router.register(r'characters', HistoricalCharacterViewSet)
router.register(r'progress', UserProgressViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
    path('test-chat/', test_chat_service, name='test-chat'),
    path('test/', TestAuthenticationView.as_view(), name='test-auth'),
]

