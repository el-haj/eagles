from django.db import models
from django.core.validators import EmailValidator

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('support', 'Technical Support'),
        ('business', 'Business Partnership'),
        ('feedback', 'Feedback'),
        ('bug_report', 'Bug Report'),
        ('feature_request', 'Feature Request'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    # Contact Information
    name = models.CharField(max_length=100, help_text="Full name of the person contacting")
    email = models.EmailField(validators=[EmailValidator()], help_text="Valid email address")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Optional phone number")
    company = models.CharField(max_length=100, blank=True, null=True, help_text="Optional company name")

    # Message Details
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    message = models.TextField(help_text="Detailed message content")

    # Status and Tracking
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='new')
    is_read = models.BooleanField(default=False, help_text="Whether the message has been read by admin")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional fields for better tracking
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="IP address of sender")
    user_agent = models.TextField(blank=True, null=True, help_text="Browser user agent")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['subject', 'created_at']),
            models.Index(fields=['is_read', 'created_at']),
        ]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d')})"

    @property
    def subject_display(self):
        return self.get_subject_display()

    @property
    def status_display(self):
        return self.get_status_display()


class ContactSettings(models.Model):
    """Settings for contact functionality"""

    # Contact Information Display
    community_description = models.TextField(blank=True, help_text="Description of the community")
    contact_email = models.EmailField(blank=True, help_text="Main contact email for the community")
    discord_server = models.URLField(blank=True, null=True, help_text="Discord server invite link")

    # Community Hours/Availability
    availability_info = models.TextField(blank=True, help_text="When the community is most active or available")

    # Community Links
    website_url = models.URLField(blank=True, null=True, help_text="Main community website")
    github_url = models.URLField(blank=True, null=True, help_text="GitHub organization/repository")
    twitter_url = models.URLField(blank=True, null=True, help_text="Twitter/X account")
    linkedin_url = models.URLField(blank=True, null=True, help_text="LinkedIn page")
    youtube_url = models.URLField(blank=True, null=True, help_text="YouTube channel")

    # Auto-response settings
    auto_response_enabled = models.BooleanField(default=True)
    auto_response_message = models.TextField(
        default="Thank you for contacting us! We have received your message and will get back to you within 24-48 hours.",
        help_text="Automatic response message sent to users"
    )

    # Admin notification settings
    admin_notification_enabled = models.BooleanField(default=True)
    admin_notification_emails = models.TextField(
        blank=True,
        help_text="Comma-separated list of admin emails to notify on new messages"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact Settings"
        verbose_name_plural = "Contact Settings"

    def __str__(self):
        return f"Contact Settings (Updated: {self.updated_at.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and ContactSettings.objects.exists():
            raise ValueError("Only one ContactSettings instance is allowed")
        super().save(*args, **kwargs)
