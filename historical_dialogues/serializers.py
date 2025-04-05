from rest_framework import serializers
from .models import (
    HistoricalCharacter, CharacterTag, CharacterAchievement,
    DialogueScenario, DialogueResponse, Quiz, QuizOption,
    UserProgress, CompletedDialogue, DiscoveredFact
)


class CharacterTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterTag
        fields = ['name']


class CharacterAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterAchievement
        fields = ['description']


class HistoricalCharacterSerializer(serializers.ModelSerializer):
    tags = CharacterTagSerializer(many=True, read_only=True)
    achievements = CharacterAchievementSerializer(many=True, read_only=True)
    portrait_url = serializers.SerializerMethodField()

    class Meta:
        model = HistoricalCharacter
        fields = [
            'id', 'name', 'period', 'short_description', 'portrait_url',
            'birth_year', 'death_year', 'nationality', 'tags', 'achievements'
        ]

    def get_portrait_url(self, obj):
        request = self.context.get('request')
        if obj.portrait and hasattr(obj.portrait, 'url'):
            return request.build_absolute_uri(obj.portrait.url)
        return None




class DialogueResponseSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = DialogueResponse
        fields = ['text', 'mood', 'fact']





class QuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ['text', 'is_correct']


class QuizSerializer(serializers.ModelSerializer):
    options = QuizOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['question', 'correct_response', 'incorrect_response', 'options']


class DialogueScenarioSerializer(serializers.ModelSerializer):
    responses = DialogueResponseSerializer(many=True, read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)

    class Meta:
        model = DialogueScenario
        fields = ['introduction', 'quiz_introduction', 'conclusion', 'responses','quizzes']


class CompletedDialogueSerializer(serializers.ModelSerializer):
    character_id = serializers.CharField(source='character.id')
    character_name = serializers.CharField(source='character.name')

    class Meta:
        model = CompletedDialogue
        fields = ['character_id', 'character_name', 'completed_at']


class DiscoveredFactSerializer(serializers.ModelSerializer):
    character_id = serializers.CharField(source='character.id')
    character_name = serializers.CharField(source='character.name')

    class Meta:
        model = DiscoveredFact
        fields = ['fact', 'character_id', 'character_name', 'discovered_at']


class UserProgressSerializer(serializers.ModelSerializer):
    
    completed_dialogues = CompletedDialogueSerializer(many=True, read_only=True)
    discovered_facts = DiscoveredFactSerializer(many=True, read_only=True)

    class Meta:
        model = UserProgress
        fields = ['user_id', 'score', 'completed_dialogues', 'discovered_facts', 'updated_at']


class UserProgressUpdateSerializer(serializers.Serializer):
    character_id = serializers.CharField()
    score = serializers.IntegerField()
    facts = serializers.ListField(child=serializers.CharField())

