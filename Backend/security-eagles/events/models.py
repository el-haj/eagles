# events/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify
from datetime import timedelta
import uuid

class EventCategory(models.Model):
    """Categories for organizing events"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Event Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def event_count(self):
        return self.events.filter(status='published', is_active=True).count()

class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('archived', 'Archived'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    EVENT_TYPE_CHOICES = [
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('webinar', 'Webinar'),
        ('meetup', 'Meetup'),
        ('seminar', 'Seminar'),
        ('training', 'Training'),
        ('networking', 'Networking'),
        ('other', 'Other'),
    ]

    RECURRENCE_CHOICES = [
        ('none', 'No Recurrence'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    # Basic Information
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(help_text="Brief description for listings")
    long_description = models.TextField(help_text="Detailed event description")
    objectives = models.TextField(blank=True, help_text="Event objectives and goals")

    # Categorization
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='other')
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list, help_text="Tags for filtering")

    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    is_featured = models.BooleanField(default=False, help_text="Featured on homepage")
    is_active = models.BooleanField(default=True)

    # Location and Platform
    is_physical = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Physical location")
    address = models.TextField(blank=True, help_text="Full address for physical events")
    platforms = ArrayField(models.CharField(max_length=100), blank=True, default=list, help_text="Online platforms")
    platform_urls = models.JSONField(blank=True, default=dict, help_text="Platform URLs as key-value pairs")

    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    timezone_info = models.CharField(max_length=50, default='UTC', help_text="Event timezone")

    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='none')
    recurrence_interval = models.PositiveIntegerField(default=1, help_text="Interval for recurrence")
    recurrence_end_date = models.DateTimeField(blank=True, null=True)
    parent_event = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='recurring_instances')

    # Registration and Capacity
    max_attendees = models.IntegerField(blank=True, null=True)
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(blank=True, null=True)
    registration_url = models.URLField(blank=True, help_text="External registration URL")

    # Organizer Information
    organizer = models.CharField(max_length=255)
    organizer_email = models.EmailField(blank=True)
    organizer_phone = models.CharField(max_length=20, blank=True)
    organizer_website = models.URLField(blank=True)

    # SEO and Meta
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    # Admin Features
    in_lights_date = models.DateTimeField(blank=True, null=True, help_text="Date when event is highlighted")
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes")

    # Tracking
    views = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['status', 'start_time']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['tags']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_highlighted(self):
        return self.in_lights_date is not None

    @property
    def status_display(self):
        """Get human-readable status with timing info"""
        if self.status != 'published':
            return self.get_status_display()

        if not self.start_time or not self.end_time:
            return self.get_status_display()

        now = timezone.now()
        if now < self.start_time:
            return 'Upcoming'
        elif self.start_time <= now <= self.end_time:
            return 'Ongoing'
        else:
            return 'Passed'

    @property
    def is_upcoming(self):
        if not self.start_time:
            return False
        return timezone.now() < self.start_time and self.status == 'published'

    @property
    def is_ongoing(self):
        if not self.start_time or not self.end_time:
            return False
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'published'

    @property
    def is_passed(self):
        if not self.end_time:
            return False
        return timezone.now() > self.end_time and self.status == 'published'

    @property
    def registration_open(self):
        if not self.registration_required:
            return False
        now = timezone.now()
        if self.registration_deadline:
            return now < self.registration_deadline and self.is_upcoming
        return self.is_upcoming

    @property
    def attendee_count(self):
        return self.registrations.filter(is_canceled=False).count()

    @property
    def spots_remaining(self):
        if not self.max_attendees:
            return None
        return max(0, self.max_attendees - self.attendee_count)

    @property
    def duration_hours(self):
        """Event duration in hours"""
        if not self.start_time or not self.end_time:
            return None
        delta = self.end_time - self.start_time
        return round(delta.total_seconds() / 3600, 1)

class EventImage(models.Model):
    """Images associated with events"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='events/images/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True, help_text="Alt text for accessibility")
    caption = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Use as main event image")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.event.title} - {self.caption or 'Image'}"

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None

class EventView(models.Model):
    """Track event page views"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='view_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user', 'ip_address']
        indexes = [
            models.Index(fields=['event', 'created_at']),
        ]

class EventRegistration(models.Model):
    """User registrations for events (optional feature)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    is_canceled = models.BooleanField(default=False)
    registration_data = models.JSONField(blank=True, default=dict, help_text="Additional registration info")
    notes = models.TextField(blank=True, help_text="User notes or special requirements")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'event']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({'Canceled' if self.is_canceled else 'Active'})"