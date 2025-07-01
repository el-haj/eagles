from django.db import models
from django.conf import settings

# Create your models here.

class Documentation(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField()
    long_description = models.TextField()
    main_markdown = models.TextField()
    links = models.JSONField(blank=True, null=True)
    meta_data = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documentations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title
