from rest_framework import serializers
from .models import (
    EscapeRoom, Room, RoomConnection, Puzzle, 
    InventoryItem, ItemLocation, GameSession, GameEvent
)

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'

class ItemLocationSerializer(serializers.ModelSerializer):
    item_details = InventoryItemSerializer(source='item', read_only=True)
    
    class Meta:
        model = ItemLocation
        fields = '__all__'

class PuzzleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Puzzle
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Remove solution from the representation for security
        if 'solution' in representation:
            representation['solution'] = None
        return representation

class PuzzleAdminSerializer(serializers.ModelSerializer):
    """Serializer with solution included for admin use"""
    class Meta:
        model = Puzzle
        fields = '__all__'

class RoomConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomConnection
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    puzzles = PuzzleSerializer(many=True, read_only=True)
    items = ItemLocationSerializer(many=True, read_only=True)
    connections_from = RoomConnectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'

class EscapeRoomSerializer(serializers.ModelSerializer):
    rooms = serializers.SerializerMethodField()
    
    class Meta:
        model = EscapeRoom
        exclude = ['created_by']
    
    def get_rooms(self, obj):
        # Only return basic room info, not all details
        rooms = obj.rooms.all()
        return [{'id': room.id, 'name': room.name, 'is_starting_room': room.is_starting_room} for room in rooms]

class EscapeRoomDetailSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)
    items = InventoryItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = EscapeRoom
        fields = '__all__'

class GameSessionSerializer(serializers.ModelSerializer):
    current_room_details = RoomSerializer(source='current_room', read_only=True)
    
    class Meta:
        model = GameSession
        fields = '__all__'
        read_only_fields = ['id', 'user', 'start_time', 'end_time', 'is_completed', 'time_spent_seconds']

class GameEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameEvent
        fields = '__all__'
        read_only_fields = ['id', 'session', 'timestamp']

class PuzzleAttemptSerializer(serializers.Serializer):
    puzzle_id = serializers.UUIDField()
    solution_attempt = serializers.JSONField()

class ItemInteractionSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    action = serializers.CharField()
    target_id = serializers.UUIDField(required=False, allow_null=True)
