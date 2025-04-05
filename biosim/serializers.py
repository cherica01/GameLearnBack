from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Experiment, 
    ExperimentVariable, 
    SimulationResult, 
    Achievement, 
    UserAchievement,
    UserNote,
    UserPreference,
    ExpectedResult
)
from django.contrib.auth import get_user_model

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ExperimentVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentVariable
        fields = [
            'id', 'name', 'display_name', 'description', 'min_value', 
            'max_value', 'default_value', 'unit', 'color', 'icon', 'order'
        ]


class ExperimentSerializer(serializers.ModelSerializer):
    variables = ExperimentVariableSerializer(many=True, read_only=True)
    
    class Meta:
        model = Experiment
        fields = [
            'id', 'title', 'description', 'difficulty', 'duration', 
            'icon', 'image', 'theory_content', 'variables', 
            'created_at', 'updated_at'
        ]


class ExperimentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing experiments."""
    
    class Meta:
        model = Experiment
        fields = ['id', 'title', 'description', 'difficulty', 'duration', 'icon', 'image', 'theory_content']


class SimulationResultSerializer(serializers.ModelSerializer):
    experiment_title = serializers.CharField(source='experiment.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SimulationResult
        fields = [
            'id', 'experiment', 'experiment_title', 'user', 'username',
            'variables_config', 'results_data', 'notes', 'duration',
            'completed', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        # Set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'title', 'description', 'icon', 'criteria', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement_details = AchievementSerializer(source='achievement', read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'user', 'achievement', 'achievement_details', 'unlocked_at']
        read_only_fields = ['id', 'user', 'unlocked_at']

class ExpectedResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpectedResult
        fields = '__all__'

class UserNoteSerializer(serializers.ModelSerializer):
    experiment_title = serializers.CharField(source='experiment.title', read_only=True)
    
    class Meta:
        model = UserNote
        fields = [
            'id', 'user', 'experiment', 'experiment_title', 
            'title', 'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            'id', 'user', 'high_quality', 'sound_enabled', 
            'tutorial_completed', 'preferences'
        ]
        read_only_fields = ['id', 'user']
    
    def create(self, validated_data):
        # Set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
