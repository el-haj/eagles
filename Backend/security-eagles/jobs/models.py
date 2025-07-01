from django.db import models
from django.conf import settings

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='job_logos/', blank=True, null=True)
    location = models.CharField(max_length=255)
    location_url = models.URLField(blank=True, null=True)
    job_type = models.CharField(max_length=100)  # e.g., Full-Time, Part-Time
    experience_level = models.CharField(max_length=100)  # e.g., Junior, Senior
    category = models.CharField(max_length=100)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    is_remote = models.BooleanField(default=False)
    application_deadline = models.DateTimeField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    closed_at = models.DateTimeField(blank=True, null=True)
    application_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class JobPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_posts')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    meta_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} applied to {self.job.title}"
