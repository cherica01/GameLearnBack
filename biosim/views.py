from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.models import User
from django.db.models import Q

from .models import (
    Experiment, 
    ExperimentVariable, 
    SimulationResult, 
    Achievement, 
    UserAchievement,
    UserNote,
    UserPreference
)

from .serializers import (
    UserSerializer,
    ExperimentSerializer,
    ExperimentListSerializer,
    ExperimentVariableSerializer,
    SimulationResultSerializer,
    AchievementSerializer,
    UserAchievementSerializer,
    UserNoteSerializer,
    UserPreferenceSerializer
)
from .permissions import IsOwnerOrReadOnly


class ExperimentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows experiments to be viewed or edited.
    """
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'difficulty']
    ordering_fields = ['title', 'difficulty', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExperimentListSerializer
        return ExperimentSerializer
    
    @action(detail=True, methods=['get'])
    def variables(self, request, pk=None):
        """Get variables for a specific experiment."""
        experiment = self.get_object()
        variables = ExperimentVariable.objects.filter(experiment=experiment)
        serializer = ExperimentVariableSerializer(variables, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get results for a specific experiment (only for the current user)."""
        experiment = self.get_object()
        results = SimulationResult.objects.filter(experiment=experiment, user=request.user)
        serializer = SimulationResultSerializer(results, many=True)
        return Response(serializer.data)


class ExperimentVariableViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows experiment variables to be viewed or edited.
    """
    queryset = ExperimentVariable.objects.all()
    serializer_class = ExperimentVariableSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = ExperimentVariable.objects.all()
        experiment_id = self.request.query_params.get('experiment', None)
        if experiment_id is not None:
            queryset = queryset.filter(experiment__id=experiment_id)
        return queryset


class SimulationResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows simulation results to be viewed or edited.
    """
    serializer_class = SimulationResultSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return SimulationResult.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def by_experiment(self, request):
        """Get results filtered by experiment."""
        experiment_id = request.query_params.get('experiment_id', None)
        if experiment_id:
            results = SimulationResult.objects.filter(
                experiment__id=experiment_id,
                user=request.user
            )
            serializer = self.get_serializer(results, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "experiment_id parameter is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows achievements to be viewed.
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows user achievements to be viewed.
    """
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return UserAchievement.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def all_with_status(self, request):
        """Get all achievements with unlocked status for the current user."""
        user = request.user
        achievements = Achievement.objects.all()
        user_achievements = UserAchievement.objects.filter(user=user)
        
        unlocked_ids = set(ua.achievement_id for ua in user_achievements)
        
        result = []
        for achievement in achievements:
            result.append({
                'id': achievement.id,
                'title': achievement.title,
                'description': achievement.description,
                'icon': achievement.icon,
                'unlocked': achievement.id in unlocked_ids
            })
        
        return Response(result)


class UserNoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user notes to be viewed or edited.
    """
    serializer_class = UserNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return UserNote.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def by_experiment(self, request):
        """Get notes filtered by experiment."""
        experiment_id = request.query_params.get('experiment_id', None)
        if experiment_id:
            notes = UserNote.objects.filter(
                experiment__id=experiment_id,
                user=request.user
            )
            serializer = self.get_serializer(notes, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "experiment_id parameter is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user preferences to be viewed or edited.
    """
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return UserPreference.objects.filter(user=user)
    
    @action(detail=False, methods=['get', 'post'])
    def me(self, request):
        """Get or create the current user's preferences."""
        user = request.user
        
        if request.method == 'GET':
            preference, created = UserPreference.objects.get_or_create(user=user)
            serializer = self.get_serializer(preference)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            preference, created = UserPreference.objects.get_or_create(user=user)
            serializer = self.get_serializer(preference, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
