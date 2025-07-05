from django.db import models
from django.conf import settings

class Lab(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    lab_url = models.URLField()
    objectives = models.TextField()
    difficulty_level = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    prize = models.CharField(max_length=255, blank=True, null=True)
    estimated_time = models.IntegerField(help_text="Estimated time in minutes")
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_labs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserLab(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_labs')
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='user_labs')
    time_spent = models.IntegerField(help_text="Time spent in minutes")
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    score = models.IntegerField()
    is_ok = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.lab}"
