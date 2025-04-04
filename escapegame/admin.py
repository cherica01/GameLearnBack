from django.contrib import admin
from .models import (
    EscapeRoom, Room, RoomConnection, Puzzle, 
    InventoryItem, ItemLocation, GameSession, GameEvent
)

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1

class PuzzleInline(admin.TabularInline):
    model = Puzzle
    extra = 1

class ItemLocationInline(admin.TabularInline):
    model = ItemLocation
    extra = 1

class RoomConnectionInline(admin.TabularInline):
    model = RoomConnection
    fk_name = 'from_room'
    extra = 1

@admin.register(EscapeRoom)
class EscapeRoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'theme', 'difficulty', 'is_published', 'created_by', 'created_at')
    list_filter = ('difficulty', 'theme', 'is_published')
    search_fields = ('title', 'description')
    inlines = [RoomInline]

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'escape_room', 'is_starting_room', 'is_final_room')
    list_filter = ('escape_room', 'is_starting_room', 'is_final_room')
    search_fields = ('name', 'description')
    inlines = [PuzzleInline, ItemLocationInline, RoomConnectionInline]

@admin.register(Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
    list_display = ('title', 'room', 'puzzle_type', 'is_required')
    list_filter = ('puzzle_type', 'is_required', 'room__escape_room')
    search_fields = ('title', 'description')

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'escape_room', 'can_be_combined')
    list_filter = ('escape_room', 'can_be_combined')
    search_fields = ('name', 'description')

@admin.register(ItemLocation)
class ItemLocationAdmin(admin.ModelAdmin):
    list_display = ('item', 'room', 'is_hidden')
    list_filter = ('room__escape_room', 'is_hidden')
    search_fields = ('item__name', 'room__name')

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'escape_room', 'start_time', 'is_completed', 'time_spent_seconds')
    list_filter = ('escape_room', 'is_completed')
    search_fields = ('user__username', 'escape_room__title')
    readonly_fields = ('id', 'start_time', 'end_time', 'time_spent_seconds', 'game_state')

@admin.register(GameEvent)
class GameEventAdmin(admin.ModelAdmin):
    list_display = ('session', 'event_type', 'timestamp')
    list_filter = ('event_type', 'session__escape_room')
    search_fields = ('session__user__username', 'event_type')
    readonly_fields = ('session', 'event_type', 'event_data', 'timestamp')
