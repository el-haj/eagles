from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


class Track(models.Model):
    """PDF tracks organized by category - no auth required"""

    CATEGORY_CHOICES = [
        ('cyber', 'Cybersecurity'),
        ('infrastructure', 'Infrastructure'),
        ('software_engineering', 'Software Engineering'),
    ]

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='beginner')
    pdf_file = models.FileField(upload_to='tracks/pdfs/')
    thumbnail = models.ImageField(upload_to='tracks/thumbnails/', blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    duration_hours = models.PositiveIntegerField(help_text="Estimated completion time in hours")
    prerequisites = models.TextField(blank=True, help_text="Required knowledge or skills")

    # Metadata
    is_active = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'level']),
            models.Index(fields=['is_active', 'category']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class LearningPath(models.Model):
    """Main learning paths like Udemy courses - requires auth"""

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    # Relationship to track
    track = models.ForeignKey(Track, related_name='learning_paths', on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField()
    short_description = models.CharField(max_length=500, help_text="Brief summary for listings")
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='beginner')
    category = models.CharField(max_length=20, choices=Track.CATEGORY_CHOICES)

    # Media
    thumbnail = models.ImageField(upload_to='learning_paths/thumbnails/', blank=True, null=True)
    intro_video_url = models.URLField(blank=True, null=True, help_text="YouTube or other video URL")

    # Learning details
    estimated_duration_hours = models.PositiveIntegerField(help_text="Total estimated completion time")
    prerequisites = models.TextField(blank=True)
    learning_objectives = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    # Management
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_learning_paths')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)

    # Statistics
    enrollment_count = models.PositiveIntegerField(default=0)
    completion_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['level', 'category']),
            models.Index(fields=['is_featured', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class LearningSection(models.Model):
    """Sections within a learning path"""

    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF Document'),
        ('markdown', 'Markdown Content'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]

    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(help_text="Order within the learning path")

    # Content
    content_type = models.CharField(max_length=15, choices=CONTENT_TYPE_CHOICES)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or other video URL")
    pdf_file = models.FileField(upload_to='learning_sections/pdfs/', blank=True, null=True)
    markdown_content = models.TextField(blank=True, help_text="Markdown formatted content")

    # Learning details
    estimated_duration_minutes = models.PositiveIntegerField(help_text="Estimated completion time in minutes")
    is_required = models.BooleanField(default=True, help_text="Required to complete the learning path")

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['learning_path', 'order']
        unique_together = ['learning_path', 'order']
        indexes = [
            models.Index(fields=['learning_path', 'order']),
            models.Index(fields=['learning_path', 'is_active']),
        ]

    def __str__(self):
        return f"{self.learning_path.title} - {self.title}"


class UserLearningProgress(models.Model):
    """Track user progress in learning paths"""

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_progress')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')

    # Progress tracking
    current_section = models.ForeignKey(LearningSection, on_delete=models.SET_NULL, null=True, blank=True)
    completed_sections = models.ManyToManyField(LearningSection, blank=True, related_name='completed_by_users')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'learning_path']
        ordering = ['-last_accessed_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['learning_path', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.learning_path.title} ({self.status})"

    def update_progress(self):
        """Calculate and update progress percentage"""
        total_sections = self.learning_path.sections.filter(is_active=True, is_required=True).count()
        if total_sections > 0:
            completed_count = self.completed_sections.filter(is_required=True).count()
            self.progress_percentage = (completed_count / total_sections) * 100

            if self.progress_percentage >= 100 and self.status != 'completed':
                self.status = 'completed'
                self.completed_at = timezone.now()
            elif self.progress_percentage > 0 and self.status == 'not_started':
                self.status = 'in_progress'
                self.started_at = timezone.now()

        self.save()


class LearningComment(models.Model):
    """Comments on learning sections (not learning paths)"""

    section = models.ForeignKey(LearningSection, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    content = models.TextField()
    is_edited = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['section', 'is_active']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.section.title}"

    @property
    def is_reply(self):
        return self.parent is not None


class LearningRating(models.Model):
    """Ratings for learning paths"""

    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_ratings')

    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    review = models.TextField(blank=True, help_text="Optional written review")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['learning_path', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['learning_path', 'rating']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.learning_path.title}: {self.rating}/5"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update learning path average rating
        self.update_learning_path_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Update learning path average rating after deletion
        self.update_learning_path_rating()

    def update_learning_path_rating(self):
        """Update the average rating for the learning path"""
        from django.db.models import Avg, Count

        rating_stats = LearningRating.objects.filter(
            learning_path=self.learning_path
        ).aggregate(
            avg_rating=Avg('rating'),
            total_ratings=Count('id')
        )

        self.learning_path.average_rating = rating_stats['avg_rating'] or 0.00
        self.learning_path.total_ratings = rating_stats['total_ratings'] or 0
        self.learning_path.save(update_fields=['average_rating', 'total_ratings'])
