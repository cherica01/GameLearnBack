from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'escape-rooms', views.EscapeRoomViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'game-sessions', views.GameSessionViewSet)
router.register(r'game-events', views.GameEventViewSet, basename='game-events')

urlpatterns = [
    path('', include(router.urls)),
]
