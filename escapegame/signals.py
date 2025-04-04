from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Puzzle, GameSession, GameEvent

@receiver(post_save, sender=GameSession)
def log_game_session_creation(sender, instance, created, **kwargs):
    """Log when a new game session is created"""
    if created:
        GameEvent.objects.create(
            session=instance,
            event_type='session_created',
            event_data={
                'escape_room_id': str(instance.escape_room.id),
                'escape_room_title': instance.escape_room.title
            }
        )

@receiver(post_save, sender=Puzzle)
def update_puzzle_solution_format(sender, instance, created, **kwargs):
    """Ensure puzzle solution is in the correct format based on puzzle type"""
    if created:
        # This is just a placeholder for any post-save processing needed for puzzles
        pass
