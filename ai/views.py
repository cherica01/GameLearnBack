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
from django.http import JsonResponse
import json
User = get_user_model()
chat_service = HistoricalCharacterChatService()
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
        Endpoint pour discuter avec un personnage historique
        """
        character = self.get_object()
        message = request.data.get('message')
        user = request.user

        if not user.is_authenticated:
            return Response(
                {"detail": "Authentification requise"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not message:
            return Response(
                {"detail": "Le message est obligatoire"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        def event_stream():
            service = HistoricalCharacterChatService()
            accumulated_content = ""  # Pour accumuler le texte final
            try:
                for chunk in service.generate_response(user, character, message):
                    # Si le chunk est un dictionnaire avec une erreur, on renvoie l'erreur immédiatement
                    if isinstance(chunk, dict) and 'error' in chunk:
                        return json.dumps({"error": chunk["error"]})
                    else:
                        # Si le chunk est un dictionnaire avec "content", on l'extrait,
                        # sinon on suppose qu'il s'agit déjà d'une chaîne
                        if isinstance(chunk, dict):
                            accumulated_content += chunk.get("content", "")
                        else:
                            accumulated_content += chunk
                return json.dumps({"content": accumulated_content})
            except Exception as e:
                print("Error in stream:", e)
                return json.dumps({"error": str(e)})

        data = event_stream()
        print("Data:", data)  
        return Response({"response": data, "mood": "neutral"})  
        return StreamingHttpResponse(d, content_type='text/event-stream')

         


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