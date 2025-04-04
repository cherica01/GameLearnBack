from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import json

from .models import SimulationResult, Achievement, UserAchievement, UserPreference

@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create UserPreference when a new user is created."""
    if created:
        UserPreference.objects.create(user=instance)

@receiver(post_save, sender=SimulationResult)
def check_achievements(sender, instance, created, **kwargs):
    """Check if any achievements should be unlocked when a simulation result is saved."""
    if not created or not instance.completed:
        return
    
    user = instance.user
    
    # Check for first_experiment achievement
    first_experiment = Achievement.objects.filter(id='first_experiment').first()
    if first_experiment and not UserAchievement.objects.filter(user=user, achievement=first_experiment).exists():
        UserAchievement.objects.create(user=user, achievement=first_experiment)
    
    # Check for optimal_conditions achievement
    if 'efficiency' in instance.results_data and instance.results_data['efficiency'] >= 0.9:
        optimal_conditions = Achievement.objects.filter(id='optimal_conditions').first()
        if optimal_conditions and not UserAchievement.objects.filter(user=user, achievement=optimal_conditions).exists():
            UserAchievement.objects.create(user=user, achievement=optimal_conditions)
    
    # Check for scientist achievement
    scientist = Achievement.objects.filter(id='scientist').first()
    if scientist:
        # Count unique experiments completed by the user
        unique_experiments = SimulationResult.objects.filter(
            user=user, 
            completed=True
        ).values('experiment').distinct().count()
        
        # Get the criteria
        criteria = json.loads(scientist.criteria)
        required_count = criteria.get('count', 5)
        
        # Check if the user has completed enough unique experiments
        if unique_experiments >= required_count and not UserAchievement.objects.filter(user=user, achievement=scientist).exists():
            UserAchievement.objects.create(user=user, achievement=scientist)
