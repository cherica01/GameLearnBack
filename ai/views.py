from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from historical_dialogues.models import (
    HistoricalCharacter, DialogueScenario,
    UserProgress, CompletedDialogue, DiscoveredFact
)
from historical_dialogues.serializers import (
    HistoricalCharacterSerializer, DialogueScenarioSerializer,
    UserProgressSerializer, UserProgressUpdateSerializer
)
from .chatgpt import HistoricalCharacterChatService
from django.http import StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
User = get_user_model()

class HistoricalCharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows historical characters to be viewed.
    """
    queryset = HistoricalCharacter.objects.all()
    serializer_class = HistoricalCharacterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow any user to view characters

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
        
    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        """
        Endpoint to chat with a historical character
        """
        character = self.get_object()
        message = request.data.get('message')
        user = request.user
        user = get_object_or_404(User, id=user.id)

        if not user:
            return Response(
                {"detail": "Authentication credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not message:
            return Response(
                {"detail": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        chat_service = HistoricalCharacterChatService()

        def stream_generator():
            for chunk in chat_service.generate_response(user, character, message):
                yield chunk
        return StreamingHttpResponse(
            streaming_content=stream_generator(),
            content_type='text/plain'
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


@api_view(['GET'])
def test_chat_service(request):
    """
    Test endpoint for the chat service
    """
    character_id = request.query_params.get('character_id')
    message = request.query_params.get('message', 'Bonjour, qui êtes-vous?')
    
    if not character_id:
        return Response(
            {"detail": "character_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        character = HistoricalCharacter.objects.get(id=character_id)
    except HistoricalCharacter.DoesNotExist:
        return Response(
            {"detail": f"Character with id {character_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
        
    chat_service = HistoricalCharacterChatService()
    
    def stream_response():
        for chunk in chat_service.generate_response(character, message):
            yield chunk
            
    return StreamingHttpResponse(
        streaming_content=stream_response(),
        content_type='text/plain'
    )