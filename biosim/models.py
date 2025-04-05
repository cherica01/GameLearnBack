from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Experiment(models.Model):
    """Model representing a scientific experiment in BioSim."""

    DIFFICULTY_CHOICES = [
        ('beginner', _('Débutant')),
        ('intermediate', _('Intermédiaire')),
        ('advanced', _('Avancé')),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(_('Titre'), max_length=100)
    description = models.TextField(_('Description'))
    difficulty = models.CharField(_('Difficulté'), max_length=20, choices=DIFFICULTY_CHOICES)
    duration = models.CharField(_('Durée'), max_length=20)
    icon = models.CharField(_('Icône'), max_length=50)
    image = models.ImageField(_('Image'), upload_to='experiments/', blank=True, null=True)
    theory_content = models.TextField(_('Contenu théorique'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Expérience')
        verbose_name_plural = _('Expériences')
        ordering = ['title']

    def __str__(self):
        return self.title


class ExperimentVariable(models.Model):
    """Model representing a variable that can be adjusted in an experiment."""

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='variables',
        verbose_name=_('Expérience')
    )
    name = models.CharField(_('Nom'), max_length=50)
    display_name = models.CharField(_('Nom affiché'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    min_value = models.FloatField(_('Valeur minimale'))
    max_value = models.FloatField(_('Valeur maximale'))
    default_value = models.FloatField(_('Valeur par défaut'))
    unit = models.CharField(_('Unité'), max_length=20, blank=True)
    color = models.CharField(_('Couleur'), max_length=20, blank=True)
    icon = models.CharField(_('Icône'), max_length=50, blank=True)
    order = models.PositiveSmallIntegerField(_('Ordre'), default=0)

    class Meta:
        verbose_name = _('Variable d\'expérience')
        verbose_name_plural = _('Variables d\'expérience')
        ordering = ['experiment', 'order', 'name']
        unique_together = ['experiment', 'name']

    def __str__(self):
        return f"{self.experiment.title} - {self.display_name}"
    
class ExpectedResult(models.Model):
    """Résultat attendu pour une variable spécifique d'une expérience."""

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='expected_results',
        verbose_name=_('Expérience')
    )
    variable = models.ForeignKey(
        ExperimentVariable,
        on_delete=models.CASCADE,
        related_name='expected_results',
        verbose_name=_('Variable')
    )
    name = models.CharField(_('Nom du résultat'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    expected_value = models.FloatField(_('Valeur attendue'))
    tolerance = models.FloatField(_('Tolérance'), default=0.0, help_text=_("Tolérance acceptée autour de la valeur attendue"))
    unit = models.CharField(_('Unité'), max_length=20, blank=True)

    class Meta:
        verbose_name = _('Résultat attendu')
        verbose_name_plural = _('Résultats attendus')
        ordering = ['experiment', 'variable__order', 'name']
        unique_together = ['experiment', 'variable']

    def __str__(self):
        return f"{self.experiment.title} - {self.variable.display_name} - {self.name}"



class SimulationResult(models.Model):
    """Model representing the results of a simulation run."""

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name=_('Expérience')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='simulation_results',
        verbose_name=_('Utilisateur')
    )
    variables_config = models.JSONField(_('Configuration des variables'))
    results_data = models.JSONField(_('Données des résultats'))
    notes = models.TextField(_('Notes'), blank=True)
    duration = models.PositiveIntegerField(_('Durée (secondes)'))
    completed = models.BooleanField(_('Terminé'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Résultat de simulation')
        verbose_name_plural = _('Résultats de simulation')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.experiment.title} - {self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class Achievement(models.Model):
    """Model representing achievements that users can unlock."""

    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(_('Titre'), max_length=100)
    description = models.TextField(_('Description'))
    icon = models.CharField(_('Icône'), max_length=50, blank=True)
    criteria = models.JSONField(_('Critères de déblocage'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Réalisation')
        verbose_name_plural = _('Réalisations')
        ordering = ['title']

    def __str__(self):
        return self.title


class UserAchievement(models.Model):
    """Model representing achievements unlocked by users."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name=_('Utilisateur')
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name=_('Réalisation')
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Réalisation utilisateur')
        verbose_name_plural = _('Réalisations utilisateur')
        ordering = ['-unlocked_at']
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.title}"


class UserNote(models.Model):
    """Model representing user notes for experiments."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Utilisateur')
    )
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='user_notes',
        verbose_name=_('Expérience')
    )
    title = models.CharField(_('Titre'), max_length=200)
    content = models.TextField(_('Contenu'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Note utilisateur')
        verbose_name_plural = _('Notes utilisateur')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class UserPreference(models.Model):
    """Model representing user preferences for the BioSim application."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='biosim_preferences',
        verbose_name=_('Utilisateur')
    )
    high_quality = models.BooleanField(_('Haute qualité graphique'), default=True)
    sound_enabled = models.BooleanField(_('Sons activés'), default=True)
    tutorial_completed = models.BooleanField(_('Tutoriel terminé'), default=False)
    preferences = models.JSONField(_('Préférences supplémentaires'), default=dict, blank=True)

    class Meta:
        verbose_name = _('Préférence utilisateur')
        verbose_name_plural = _('Préférences utilisateur')

    def __str__(self):
        return f"Préférences de {self.user.username}"
