# services.py
import logging
import os
from typing import Dict, Generator, Optional
import json
from django.core.cache import cache
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from .models import ChatHistory

from historical_dialogues.models import HistoricalCharacter, DialogueScenario, DialogueResponse
from django.contrib.auth import get_user_model
User = get_user_model()

logger = logging.getLogger(__name__)
load_dotenv()

class HistoricalCharacterChatService:
    """Service de chat avec personnage historique avec gestion d'humeur"""
    
    MOOD_MAPPING = {
        'happy': 'content et enthousiaste',
        'neutral': 'neutre et réfléchi',
        'thinking': 'pensif et sérieux',
        'surprised': 'surpris et intrigué'
    }

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.cache_timeout = 3600  # 1h cache

    def _get_character_prompt(self, character: HistoricalCharacter) -> str:
        """Construit le prompt système pour le personnage"""
        cache_key = f"character_prompt:{character.id}"
        cached_prompt = cache.get(cache_key)
        
        if cached_prompt:
            return cached_prompt

        try:
            # scenario = character.dialogue_scenario
            prompt = f"""
            Tu incarnes {character.name}, {character.short_description}.
            Période: {character.period}
            
            Ton comportement:
            - Utilise un langage d'époque approprié
            - Tes connaissances se limitent à ton époque
            - Adapte ton humeur selon le contexte

            Format des réponses:
            - Sois naturel et conversationnel
            - Utilise des détails historiques précis
            - Limite tes réponses à 2-3 phrases maximum
            - Pose 1 questio    n après 3 réponses
            Envoie comme message d'introduction 'Bonjour, je suis {character.name}. Que veux-tu savoir sur {character.period}?'
            """
            
            cache.set(cache_key, prompt, self.cache_timeout)
            return prompt
            
        except DialogueScenario.DoesNotExist:
            logger.error(f"No dialogue scenario for character {character.id}")
            return f"Tu es {character.name}. Parle comme un personnage historique."

    def _detect_mood(self, message: str) -> str:
        """Détecte l'humeur du message utilisateur"""
        mood = 'neutral'
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyse le ton du message et réponds UNIQUEMENT par un de ces mots: happy, neutral, thinking, surprised"
                    },
                    {
                        "role": "user", 
                        "content": message
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            mood = response.choices[0].message.content.lower()
            return mood if mood in self.MOOD_MAPPING else 'neutral'
            
        except Exception as e:
            logger.warning(f"Mood detection failed: {str(e)}")
            return mood
        
    def get_chat_history(self, user, character):
            if not user or not user.id:
                return []
            return list(ChatHistory.objects.filter(user=user, character= character).order_by('-timestamp').values('prompt', 'response')[:3])

    def _get_historical_context(self, character: HistoricalCharacter) -> list[ChatCompletionMessageParam]:
        """Récupère le contexte historique du personnage"""
        context_messages: list[ChatCompletionMessageParam] = []
        
        # Ajout des réalisations
        for achievement in character.achievements.all()[:3]:
            context_messages.append({
                "role": "system",
                "content": f"Realisation importante: {achievement.description}"
            })
        
        # Ajout des tags
        tags = [tag.name for tag in character.tags.all()[:5]]
        if tags:
            context_messages.append({
                "role": "system",
                "content": f"Mots-clés descriptifs: {', '.join(tags)}"
            })
            
        return context_messages

    def generate_response(
        self,
        user,
        character: HistoricalCharacter,
        message: str,  ) -> Generator[str, None, None]:

        try:
            # 1. Préparation du contexte
            mood = self._detect_mood(message)
            mood_description = self.MOOD_MAPPING.get(mood, 'neutre')
            
            system_prompt = self._get_character_prompt(character) + """\n\nTon humeur actuelle: {mood_description} + 
               
              """
            
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                *self._get_historical_context(character)
            ]
            history = self.get_chat_history(user, character)
            # 2. Ajout de l'historique si fourni                        # 2. Ajout de l'historique si fourni
            for h in reversed(history):
                messages.extend([
                    {"role": "user", "content": h['prompt']},
                    {"role": "assistant", "content": h['response']}
                ])

            # Remplacer l'ajout incorrect du message par :
            messages.append({"role": "user", "content": message})


            # 3. Appel à l'API OpenAI
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=0.7,
                stream=True,
            )


            
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:  
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

           
            ChatHistory.objects.create(
                user=user,
                character=character,
                prompt=json.dumps(message),
                response=full_response,
                context= {}
            )

            self._save_dialogue_response(character, message, full_response, mood)
           

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            yield "Désolé, une erreur est survenue. Pouvez-vous répéter ?"

    def _save_dialogue_response(
        self, 
        character: HistoricalCharacter,
        user_message: str,
        response: str,
        mood: str
    ) -> None:
        """Sauvegarde une réponse type pour réutilisation future"""
        try:
            scenario = character.dialogue_scenario
            DialogueResponse.objects.create(
                scenario=scenario,
                text=response,
                mood=mood,
                fact=self._extract_fact_from_response(response)
            )
        except Exception as e:
            logger.warning(f"Failed to save dialogue response: {str(e)}")

    def _extract_fact_from_response(self, response: str) -> Optional[str]:
        """Extrait un fait historique de la réponse"""
        try:
            facts = [s for s in response.split('.') if any(kw in s.lower() for kw in ['savoir', 'fait', 'histoire'])]
            return facts[0][:255] + '...' if facts else None
        except:
            return None