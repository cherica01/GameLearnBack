from django.db import models
from django.conf import settings
# Create your models here.
class ChatHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    context = models.JSONField(default=dict)  # Pour stocker le contexte de session

    class Meta:
        ordering = ['-timestamp']