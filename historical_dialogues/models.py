from django.db import models
from django.utils.text import slugify
from django.conf import settings


class HistoricalCharacter(models.Model):
    """Model representing a historical character."""
    id = models.SlugField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    period = models.CharField(max_length=100)
    short_description = models.TextField()
    portrait = models.ImageField(upload_to='historical_characters/')
    birth_year = models.IntegerField()
    death_year = models.IntegerField(null=True, blank=True)
    nationality = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class CharacterTag(models.Model):
    """Model representing tags for historical characters."""
    character = models.ForeignKey(HistoricalCharacter, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.character.name} - {self.name}"

    class Meta:
        unique_together = ['character', 'name']


class CharacterAchievement(models.Model):
    """Model representing achievements of historical characters."""
    character = models.ForeignKey(HistoricalCharacter, on_delete=models.CASCADE, related_name='achievements')
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.character.name} - {self.description[:30]}"


class DialogueScenario(models.Model):
    """Model representing a dialogue scenario for a historical character."""
    character = models.OneToOneField(HistoricalCharacter, on_delete=models.CASCADE, related_name='dialogue_scenario')
    introduction = models.TextField()
    quiz_introduction = models.TextField()
    conclusion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dialogue for {self.character.name}"


class DialogueResponse(models.Model):
    """Model representing predefined responses in a dialogue scenario."""
    scenario = models.ForeignKey(DialogueScenario, on_delete=models.CASCADE, related_name='responses')
    text = models.TextField()
    MOOD_CHOICES = [
        ('neutral', 'Neutral'),
        ('happy', 'Happy'),
        ('thinking', 'Thinking'),
        ('surprised', 'Surprised'),
    ]
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='neutral')
    fact = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Response for {self.scenario.character.name}: {self.text[:30]}..."


class Quiz(models.Model):
    """Model representing quizzes in a dialogue scenario."""
    scenario = models.ForeignKey(DialogueScenario, on_delete=models.CASCADE, related_name='quizzes')
    question = models.TextField()
    correct_response = models.TextField()
    incorrect_response = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Quiz for {self.scenario.character.name}: {self.question[:30]}..."

    class Meta:
        ordering = ['order']


class QuizOption(models.Model):
    """Model representing options for quiz questions."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quiz.scenario.character.name} - {self.text[:30]}... ({'Correct' if self.is_correct else 'Incorrect'})"


class UserProgress(models.Model):
    """Model representing a user's progress in historical dialogues."""
    user_id = models.CharField(max_length=100)
    score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progress for user {self.user_id}: {self.score} points"


class CompletedDialogue(models.Model):
    """Model representing completed dialogues by users."""
    progress = models.ForeignKey(UserProgress, on_delete=models.CASCADE, related_name='completed_dialogues')
    character = models.ForeignKey(HistoricalCharacter, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.progress.user_id} completed {self.character.name}"

    class Meta:
        unique_together = ['progress', 'character']


class DiscoveredFact(models.Model):
    """Model representing facts discovered by users."""
    progress = models.ForeignKey(UserProgress, on_delete=models.CASCADE, related_name='discovered_facts')
    fact = models.TextField()
    character = models.ForeignKey(HistoricalCharacter, on_delete=models.CASCADE)
    discovered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.progress.user_id} discovered fact about {self.character.name}: {self.fact[:30]}..."

    class Meta:
        unique_together = ['progress', 'fact']

