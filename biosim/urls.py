from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'experiments', views.ExperimentViewSet)
router.register(r'variables', views.ExperimentVariableViewSet)
router.register(r'results', views.SimulationResultViewSet, basename='results')
router.register(r'achievements', views.AchievementViewSet)
router.register(r'user-achievements', views.UserAchievementViewSet, basename='user-achievements')
router.register(r'notes', views.UserNoteViewSet, basename='notes')
router.register(r'preferences', views.UserPreferenceViewSet, basename='preferences')

urlpatterns = [
    path('', include(router.urls)),
]
