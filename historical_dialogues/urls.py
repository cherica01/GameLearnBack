from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistoricalCharacterViewSet, UserProgressViewSet

router = DefaultRouter()
router.register(r'characters', HistoricalCharacterViewSet)
router.register(r'progress', UserProgressViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
]

