from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify

class NewsCategory(models.Model):
    """Categories for organizing news articles"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code for category")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "News Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class News(models.Model):
    """Enhanced News model for community website"""

    # Status choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    # Priority choices
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Basic Information
    title = models.CharField(max_length=255, help_text="News article title")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True, help_text="Optional subtitle")
    author = models.CharField(max_length=100, help_text="Author name")

    # Content
    summary = models.TextField(max_length=500, help_text="Brief summary for previews (max 500 chars)")
    content = models.TextField(help_text="Full article content (supports markdown)")
    excerpt = models.TextField(max_length=300, blank=True, help_text="Auto-generated or custom excerpt")

    # Categorization
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='news_articles')
    tags = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        help_text="List of tags for better searchability"
    )

    # Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    is_featured = models.BooleanField(default=False, help_text="Feature this article on homepage")
    is_breaking = models.BooleanField(default=False, help_text="Mark as breaking news")

    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_news')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Engagement
    views = models.PositiveIntegerField(default=0, help_text="Number of times this news item has been viewed")
    likes = models.PositiveIntegerField(default=0, help_text="Number of likes")

    # SEO
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords")

    class Meta:
        verbose_name_plural = "News Articles"
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['is_breaking', 'status']),
        ]

    def save(self, *args, **kwargs):
        # Auto-generate slug from title
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-generate excerpt if not provided
        if not self.excerpt and self.summary:
            self.excerpt = self.summary[:297] + "..." if len(self.summary) > 300 else self.summary

        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def increment_views(self):
        """Increment view count atomically"""
        self.views = models.F('views') + 1
        self.save(update_fields=['views'])

    def increment_likes(self):
        """Increment like count atomically"""
        self.likes = models.F('likes') + 1
        self.save(update_fields=['likes'])

    @property
    def is_published(self):
        """Check if article is published"""
        return self.status == 'published' and self.published_at is not None

    @property
    def reading_time(self):
        """Estimate reading time in minutes"""
        word_count = len(self.content.split())
        return max(1, word_count // 200)  # Assuming 200 words per minute

    def get_absolute_url(self):
        """Get the absolute URL for this news article"""
        return reverse('news:detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class NewsImage(models.Model):
    """Enhanced model for news article images"""
    news = models.ForeignKey(News, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news_images/%Y/%m/', help_text="Upload news article images")
    caption = models.CharField(max_length=255, blank=True, help_text="Image caption")
    alt_text = models.CharField(max_length=255, blank=True, help_text="Alt text for accessibility")
    is_featured = models.BooleanField(default=False, help_text="Use as featured image")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "News Image"
        verbose_name_plural = "News Images"

    def __str__(self):
        return f"Image for {self.news.title} - {self.caption or 'No caption'}"

class NewsComment(models.Model):
    """Comments on news articles"""
    news = models.ForeignKey(News, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000, help_text="Comment content")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_approved = models.BooleanField(default=True, help_text="Approve comment for display")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "News Comment"
        verbose_name_plural = "News Comments"

    def __str__(self):
        return f"Comment by {self.author.username} on {self.news.title}"

class NewsLike(models.Model):
    """Track user likes on news articles"""
    news = models.ForeignKey(News, related_name='user_likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('news', 'user')
        verbose_name = "News Like"
        verbose_name_plural = "News Likes"

    def __str__(self):
        return f"{self.user.username} likes {self.news.title}"

class NewsView(models.Model):
    """Track individual news article views"""
    news = models.ForeignKey(News, related_name='view_records', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "News View"
        verbose_name_plural = "News Views"
        indexes = [
            models.Index(fields=['news', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]

    def __str__(self):
        user_info = self.user.username if self.user else self.ip_address
        return f"View by {user_info} on {self.news.title}"
