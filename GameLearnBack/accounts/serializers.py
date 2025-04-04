from rest_framework import serializers
from .models import User, StudentProfile, TeacherProfile

class UserSerializer(serializers.ModelSerializer):
        required=False
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "password"]
        extra_kwargs = {"password": {"write_only": True}}

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ["student_id", "parcours"]

class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ["teacher_id", "matiere"]