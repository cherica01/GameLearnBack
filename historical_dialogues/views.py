from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    HistoricalCharacter, DialogueScenario,
    UserProgress, CompletedDialogue, DiscoveredFact
)
from .serializers import (
    HistoricalCharacterSerializer, DialogueScenarioSerializer,
    UserProgressSerializer, UserProgressUpdateSerializer
)


class HistoricalCharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows historical characters to be viewed.
    """
    queryset = HistoricalCharacter.objects.all()
    serializer_class = HistoricalCharacterSerializer

    @action(detail=True, methods=['get'])
    def dialogue(self, request, pk=None):
        character = self.get_object()
        try:
            dialogue_scenario = character.dialogue_scenario
            serializer = DialogueScenarioSerializer(dialogue_scenario)
            return Response(serializer.data)
        except DialogueScenario.DoesNotExist:
            return Response(
                {"detail": f"No dialogue scenario found for {character.name}"},
                status=status.HTTP_404_NOT_FOUND
            )


class UserProgressViewSet(viewsets.ViewSet):
    """
    API endpoint that allows user progress to be viewed and updated.
    """
    def retrieve(self, request, pk=None):
        # pk is the user_id
        progress, created = UserProgress.objects.get_or_create(user_id=pk)
        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # pk is the user_id
        serializer = UserProgressUpdateSerializer(data=request.data)
        if serializer.is_valid():
            progress, created = UserProgress.objects.get_or_create(user_id=pk)
            
            # Update score
            progress.score += serializer.validated_data['score']
            progress.save()
            
            # Add completed dialogue
            character_id = serializer.validated_data['character_id']
            character = get_object_or_404(HistoricalCharacter, id=character_id)
            CompletedDialogue.objects.get_or_create(progress=progress, character=character)
            
            # Add discovered facts
            facts = serializer.validated_data['facts']
            for fact_text in facts:
                DiscoveredFact.objects.get_or_create(
                    progress=progress,
                    character=character,
                    fact=fact_text
                )
            
            # Return updated progress
            response_serializer = UserProgressSerializer(progress)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

