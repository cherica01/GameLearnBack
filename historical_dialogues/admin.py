from django.contrib import admin
from .models import (
    HistoricalCharacter, CharacterTag, CharacterAchievement,
    DialogueScenario, DialogueResponse, Quiz, QuizOption,
    UserProgress, CompletedDialogue, DiscoveredFact,
)


class CharacterTagInline(admin.TabularInline):
    model = CharacterTag
    extra = 1


class CharacterAchievementInline(admin.TabularInline):
    model = CharacterAchievement
    extra = 1


@admin.register(HistoricalCharacter)
class HistoricalCharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'period', 'nationality', 'birth_year', 'death_year')
    search_fields = ('name', 'period', 'nationality')
    list_filter = ('nationality',)
    prepopulated_fields = {'id': ('name',)}
    inlines = [CharacterTagInline, CharacterAchievementInline]


class DialogueResponseInline(admin.TabularInline):
    model = DialogueResponse
    extra = 0
    show_change_link = True


class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 0
    show_change_link = True


@admin.register(DialogueScenario)
class DialogueScenarioAdmin(admin.ModelAdmin):
    list_display = ('character', 'responses_count', 'quizzes_count')
    search_fields = ('character__name', 'introduction', 'conclusion')
    inlines = [DialogueResponseInline, QuizInline]

    def responses_count(self, obj):
        return obj.responses.count()
    responses_count.short_description = 'Responses'

    def quizzes_count(self, obj):
        return obj.quizzes.count()
    quizzes_count.short_description = 'Quizzes'


class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 4


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('get_character_name', 'question_preview', 'options_count', 'order')
    search_fields = ('question', 'correct_response', 'incorrect_response')
    list_filter = ('scenario__character',)
    inlines = [QuizOptionInline]

    def get_character_name(self, obj):
        return obj.scenario.character.name
    get_character_name.short_description = 'Character'
    get_character_name.admin_order_field = 'scenario__character__name'

    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'

    def options_count(self, obj):
        return obj.options.count()
    options_count.short_description = 'Options'


class CompletedDialogueInline(admin.TabularInline):
    model = CompletedDialogue
    extra = 0


class DiscoveredFactInline(admin.TabularInline):
    model = DiscoveredFact
    extra = 0


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'score', 'completed_dialogues_count', 'discovered_facts_count', 'updated_at')
    search_fields = ('user_id',)
    inlines = [CompletedDialogueInline, DiscoveredFactInline]

    def completed_dialogues_count(self, obj):
        return obj.completed_dialogues.count()
    completed_dialogues_count.short_description = 'Completed Dialogues'

    def discovered_facts_count(self, obj):
        return obj.discovered_facts.count()
    discovered_facts_count.short_description = 'Discovered Facts'


# Register remaining models
admin.site.register(QuizOption)
admin.site.register(CompletedDialogue)
admin.site.register(DiscoveredFact)

