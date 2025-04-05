from django.contrib import admin
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

class ExperimentVariableInline(admin.TabularInline):
    model = ExperimentVariable
    extra = 1

@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty', 'duration')
    list_filter = ('difficulty',)
    search_fields = ('title', 'description')
    inlines = [ExperimentVariableInline]

@admin.register(ExperimentVariable)
class ExperimentVariableAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'experiment', 'min_value', 'max_value', 'default_value')
    list_filter = ('experiment',)
    search_fields = ('name', 'display_name')
    ordering = ('experiment', 'order', 'name')

@admin.register(SimulationResult)
class SimulationResultAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'user', 'duration', 'completed', 'created_at')
    list_filter = ('experiment', 'completed')
    search_fields = ('user__username', 'experiment__title')
    date_hierarchy = 'created_at'

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title', 'description')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'unlocked_at')
    list_filter = ('achievement',)
    search_fields = ('user__username', 'achievement__title')
    date_hierarchy = 'unlocked_at'

@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'experiment', 'title', 'created_at', 'updated_at')
    list_filter = ('experiment',)
    search_fields = ('user__username', 'title', 'content')
    date_hierarchy = 'updated_at'

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'high_quality', 'sound_enabled', 'tutorial_completed')
    list_filter = ('high_quality', 'sound_enabled', 'tutorial_completed')
    search_fields = ('user__username',)


admin.site.register(ExpectedResult)