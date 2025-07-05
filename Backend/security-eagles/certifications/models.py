from django.db import models
from django.conf import settings

class Certification(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=100)
    is_pro = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    badge_pic = models.ImageField(upload_to='certification_badges/', blank=True, null=True)
    test_url = models.CharField(max_length=500)
    required_completion = models.FloatField()
    is_active = models.BooleanField(default=True)
    recurring_time = models.IntegerField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_certifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name
    
class UserCertification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_certifications'
    )
    certification = models.ForeignKey(
        Certification,
        on_delete=models.CASCADE,
        related_name='user_certifications'
    )
    done_at = models.DateTimeField(null=True, blank=True)
    completion = models.FloatField(null=True, blank=True)
    last_attend = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['certification']),
            models.Index(fields=['done_at']),
        ]
        unique_together = ('user', 'certification')

    def __str__(self):
        return f"{self.user} - {self.certification}"