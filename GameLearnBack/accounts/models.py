from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Étudiant"
        TEACHER = "teacher", "Enseignant"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.TEACHER
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(max_length=20, unique=True)
    parcours = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - Étudiant ({self.parcours})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    teacher_id = models.CharField(max_length=20, unique=True)
    matiere = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - Enseignant ({self.matiere})"