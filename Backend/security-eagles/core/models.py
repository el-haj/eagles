
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



class User(AbstractUser):
    
    sso_provider = models.CharField(max_length=255, blank=True, null=True)
    sso_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    score = models.IntegerField(default=0)
    cv_url = models.URLField(blank=True, null=True)
    profile_pic = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=20, choices=[('public', 'Public'), ('private', 'Private')], default='public')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    meta_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser
