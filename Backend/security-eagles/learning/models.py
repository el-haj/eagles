from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
User = get_user_model()

class LearningPath(models.Model):
    title = models.CharField(max_length=255)
    objectives = models.TextField()
    category = models.CharField(max_length=100)
    tags = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    estimated_time = models.IntegerField(help_text="Estimated time in minutes")
    meta_data = models.JSONField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class LearningPDF(models.Model):
    learning_path = models.ForeignKey(LearningPath, related_name='pdfs', on_delete=models.CASCADE)
    order_index = models.IntegerField()
    page_count = models.IntegerField()
    file = models.FileField(upload_to='learning_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    meta_data = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['order_index']

    def __str__(self):
        return f"{self.learning_path.title} - PDF {self.order_index}"

class UserLearning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    pdf = models.ForeignKey(LearningPDF, null=True, blank=True, on_delete=models.SET_NULL)
    page = models.IntegerField(default=0)
    completion = models.FloatField(default=0.0)
    meta_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'learning_path')

    def __str__(self):
        return f"{self.user.username} - {self.learning_path.title}"
