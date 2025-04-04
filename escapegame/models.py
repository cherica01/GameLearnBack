from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid
import json

class EscapeRoom(models.Model):
    """Model representing an escape room game"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.IntegerField(choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], default=1)
    theme = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    grade_level = models.CharField(max_length=50)
    time_limit_minutes = models.IntegerField(default=60)
    cover_image = models.ImageField(upload_to='escape_rooms/covers/', null=True, blank=True)
    background_image = models.ImageField(upload_to='escape_rooms/backgrounds/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_escape_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Escape Room')
        verbose_name_plural = _('Escape Rooms')

class Room(models.Model):
    """Model representing a room within an escape room game"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    escape_room = models.ForeignKey(EscapeRoom, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100)
    description = models.TextField()
    background_image = models.ImageField(upload_to='escape_rooms/rooms/', null=True, blank=True)
    position_x = models.IntegerField(default=0)  # For map positioning
    position_y = models.IntegerField(default=0)  # For map positioning
    is_starting_room = models.BooleanField(default=False)
    is_final_room = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.escape_room.title} - {self.name}"
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')

class RoomConnection(models.Model):
    """Model representing connections between rooms"""
    from_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='connections_from')
    to_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='connections_to')
    is_locked = models.BooleanField(default=True)
    unlock_condition = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"Connection from {self.from_room.name} to {self.to_room.name}"
    
    class Meta:
        unique_together = ('from_room', 'to_room')
        verbose_name = _('Room Connection')
        verbose_name_plural = _('Room Connections')

class PuzzleType(models.TextChoices):
    CODE = 'CODE', _('Code Entry')
    SEQUENCE = 'SEQUENCE', _('Sequence Puzzle')
    SWITCHES = 'SWITCHES', _('Switches Puzzle')
    TERMINAL = 'TERMINAL', _('Terminal Puzzle')
    ITEM_COMBINATION = 'ITEM_COMBINATION', _('Item Combination')
    QUIZ = 'QUIZ', _('Quiz')
    CUSTOM = 'CUSTOM', _('Custom Puzzle')

class Puzzle(models.Model):
    """Model representing a puzzle within a room"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='puzzles')
    title = models.CharField(max_length=100)
    description = models.TextField()
    puzzle_type = models.CharField(max_length=20, choices=PuzzleType.choices)
    configuration = models.JSONField()  # Stores puzzle-specific configuration
    solution = models.JSONField()  # Stores the solution
    hint_text = models.TextField(blank=True)
    position_x = models.IntegerField(default=0)  # For positioning in the room
    position_y = models.IntegerField(default=0)  # For positioning in the room
    is_required = models.BooleanField(default=True)
    educational_content = models.TextField(blank=True)  # Educational information related to the puzzle
    
    def __str__(self):
        return f"{self.room.name} - {self.title}"
    
    class Meta:
        verbose_name = _('Puzzle')
        verbose_name_plural = _('Puzzles')

class InventoryItem(models.Model):
    """Model representing an item that can be collected in the game"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    escape_room = models.ForeignKey(EscapeRoom, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='escape_rooms/items/', null=True, blank=True)
    can_be_combined = models.BooleanField(default=False)
    combination_result = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='components')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Inventory Item')
        verbose_name_plural = _('Inventory Items')

class ItemLocation(models.Model):
    """Model representing where an item is located in the game"""
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='locations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='items')
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    reveal_condition = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.item.name} in {self.room.name}"
    
    class Meta:
        verbose_name = _('Item Location')
        verbose_name_plural = _('Item Locations')

class GameSession(models.Model):
    """Model representing a player's game session"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='escape_game_sessions')
    escape_room = models.ForeignKey(EscapeRoom, on_delete=models.CASCADE, related_name='sessions')
    current_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='current_sessions', null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    time_spent_seconds = models.IntegerField(default=0)
    hints_used = models.IntegerField(default=0)
    game_state = models.JSONField(default=dict)  # Stores the current state of the game
    
    def __str__(self):
        return f"{self.user.username}'s session for {self.escape_room.title}"
    
    class Meta:
        verbose_name = _('Game Session')
        verbose_name_plural = _('Game Sessions')
    
    def get_collected_items(self):
        """Returns a list of collected items from the game state"""
        return self.game_state.get('inventory', [])
    
    def get_solved_puzzles(self):
        """Returns a list of solved puzzles from the game state"""
        return self.game_state.get('solved_puzzles', [])
    
    def get_unlocked_rooms(self):
        """Returns a list of unlocked rooms from the game state"""
        return self.game_state.get('unlocked_rooms', [])
    
    def add_to_inventory(self, item_id):
        """Adds an item to the player's inventory"""
        if 'inventory' not in self.game_state:
            self.game_state['inventory'] = []
        
        if item_id not in self.game_state['inventory']:
            self.game_state['inventory'].append(item_id)
            self.save()
    
    def mark_puzzle_solved(self, puzzle_id):
        """Marks a puzzle as solved"""
        if 'solved_puzzles' not in self.game_state:
            self.game_state['solved_puzzles'] = []
        
        if puzzle_id not in self.game_state['solved_puzzles']:
            self.game_state['solved_puzzles'].append(puzzle_id)
            self.save()
    
    def unlock_room(self, room_id):
        """Marks a room as unlocked"""
        if 'unlocked_rooms' not in self.game_state:
            self.game_state['unlocked_rooms'] = []
        
        if room_id not in self.game_state['unlocked_rooms']:
            self.game_state['unlocked_rooms'].append(room_id)
            self.save()

class GameEvent(models.Model):
    """Model for tracking events during gameplay"""
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50)
    event_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = _('Game Event')
        verbose_name_plural = _('Game Events')
