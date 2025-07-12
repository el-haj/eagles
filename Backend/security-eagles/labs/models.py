from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class Lab(models.Model):
    """Lab model representing external practice environments"""

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    CATEGORY_CHOICES = [
        ('web_security', 'Web Security'),
        ('network_security', 'Network Security'),
        ('cryptography', 'Cryptography'),
        ('forensics', 'Digital Forensics'),
        ('reverse_engineering', 'Reverse Engineering'),
        ('penetration_testing', 'Penetration Testing'),
        ('malware_analysis', 'Malware Analysis'),
        ('incident_response', 'Incident Response'),
        ('compliance', 'Compliance & Governance'),
        ('cloud_security', 'Cloud Security'),
        ('mobile_security', 'Mobile Security'),
        ('iot_security', 'IoT Security'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('deprecated', 'Deprecated'),
    ]

    # Basic Information
    name = models.CharField(max_length=255)
    description = models.TextField()
    objectives = models.TextField(help_text="Learning objectives and goals")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')

    # Lab Configuration
    lab_url = models.URLField(help_text="URL to the external lab environment")
    external_lab_id = models.CharField(max_length=255, unique=True, help_text="Unique ID used by the external lab system")
    estimated_time = models.IntegerField(validators=[MinValueValidator(1)], help_text="Estimated completion time in minutes")

    # Scoring System
    max_score = models.IntegerField(default=100, validators=[MinValueValidator(1), MaxValueValidator(1000)], help_text="Maximum score possible for this lab")
    min_score = models.IntegerField(default=70, validators=[MinValueValidator(0)], help_text="Minimum score required to pass this lab")
    perfect_score_bonus = models.IntegerField(default=0, help_text="Extra points awarded for achieving perfect score")

    # Points and Rewards
    base_points = models.IntegerField(default=10, validators=[MinValueValidator(0)], help_text="Base points awarded for passing this lab")
    bonus_points = models.IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Additional bonus points for exceptional performance")

    # Access Control
    cooldown_minutes = models.IntegerField(default=60, validators=[MinValueValidator(0)], help_text="Cooldown time in minutes before user can retake the lab")
    max_attempts_per_day = models.IntegerField(default=3, validators=[MinValueValidator(1)], help_text="Maximum attempts allowed per day")
    requires_prerequisites = models.BooleanField(default=False, help_text="Whether this lab requires completing prerequisite labs")
    prerequisite_labs = models.ManyToManyField('self', blank=True, symmetrical=False, help_text="Labs that must be completed before accessing this lab")

    # Metadata
    tags = models.JSONField(default=list, blank=True, help_text="Tags for categorization and search")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes or instructions")
    is_featured = models.BooleanField(default=False, help_text="Whether to feature this lab prominently")

    # Management
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_labs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'difficulty_level']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['is_featured', '-created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_difficulty_level_display()})"

    def clean(self):
        """Validate model data"""
        from django.core.exceptions import ValidationError
        if self.min_score > self.max_score:
            raise ValidationError("Minimum score cannot be greater than maximum score")

    def is_accessible_by_user(self, user):
        """Check if user can access this lab based on prerequisites"""
        if not self.requires_prerequisites:
            return True

        # Check if user has completed all prerequisite labs
        prerequisite_ids = self.prerequisite_labs.values_list('id', flat=True)
        completed_prerequisites = UserLab.objects.filter(
            user=user,
            lab_id__in=prerequisite_ids,
            is_passed=True
        ).values_list('lab_id', flat=True).distinct()

        return set(prerequisite_ids) <= set(completed_prerequisites)

    def get_user_cooldown_remaining(self, user):
        """Get remaining cooldown time for user in minutes"""
        if self.cooldown_minutes == 0:
            return 0

        latest_attempt = UserLab.objects.filter(
            user=user,
            lab=self,
            cooldown_until__isnull=False
        ).order_by('-created_at').first()

        if not latest_attempt or not latest_attempt.cooldown_until:
            return 0

        now = timezone.now()
        if latest_attempt.cooldown_until <= now:
            return 0

        remaining_seconds = (latest_attempt.cooldown_until - now).total_seconds()
        return max(0, int(remaining_seconds / 60))

    def get_user_attempts_today(self, user):
        """Get number of attempts user has made today"""
        today = timezone.now().date()
        return UserLab.objects.filter(
            user=user,
            lab=self,
            created_at__date=today
        ).count()

    def can_user_attempt(self, user):
        """Check if user can attempt this lab right now"""
        # Check if lab is active
        if self.status != 'active':
            return False, "Lab is not currently available"

        # Check prerequisites
        if not self.is_accessible_by_user(user):
            return False, "Prerequisites not met"

        # Check cooldown
        cooldown_remaining = self.get_user_cooldown_remaining(user)
        if cooldown_remaining > 0:
            return False, f"Cooldown active. Try again in {cooldown_remaining} minutes"

        # Check daily attempts
        attempts_today = self.get_user_attempts_today(user)
        if attempts_today >= self.max_attempts_per_day:
            return False, f"Daily attempt limit reached ({self.max_attempts_per_day})"

        return True, "Can attempt"

class UserLab(models.Model):
    """User's lab attempt record"""

    ATTEMPT_STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('timeout', 'Timed Out'),
    ]

    # Core Relations
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lab_attempts')
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='user_attempts')

    # Attempt Details
    attempt_number = models.PositiveIntegerField(help_text="Sequential attempt number for this user-lab combination")
    status = models.CharField(max_length=15, choices=ATTEMPT_STATUS_CHOICES, default='started')

    # Timing
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(null=True, blank=True, help_text="Actual time spent in minutes")

    # Scoring
    score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    max_possible_score = models.IntegerField(help_text="Max score possible at time of attempt")
    is_passed = models.BooleanField(default=False, help_text="Whether the attempt passed the minimum score")
    is_perfect_score = models.BooleanField(default=False, help_text="Whether user achieved perfect score")

    # Points and Rewards
    base_points_earned = models.IntegerField(default=0, help_text="Base points earned for this attempt")
    bonus_points_earned = models.IntegerField(default=0, help_text="Bonus points earned for this attempt")
    total_points_earned = models.IntegerField(default=0, help_text="Total points earned for this attempt")

    # External System Integration
    external_attempt_id = models.CharField(max_length=255, blank=True, null=True, help_text="Attempt ID from external lab system")
    external_session_token = models.CharField(max_length=500, blank=True, null=True, help_text="Session token for external system")
    redirect_token = models.CharField(max_length=255, blank=True, null=True, help_text="Secure token for lab redirection")

    # Cooldown Management
    cooldown_until = models.DateTimeField(blank=True, null=True, help_text="User cannot retake until this time")

    # Metadata
    user_agent = models.TextField(blank=True, null=True, help_text="User agent string")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="User's IP address")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the attempt")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'lab', 'attempt_number']
        indexes = [
            models.Index(fields=['user', 'lab', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['is_passed', '-created_at']),
            models.Index(fields=['redirect_token']),
            models.Index(fields=['external_attempt_id']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.lab.name} (Attempt #{self.attempt_number})"

    def save(self, *args, **kwargs):
        # Auto-set attempt number if not provided
        if not self.attempt_number:
            last_attempt = UserLab.objects.filter(
                user=self.user,
                lab=self.lab
            ).order_by('-attempt_number').first()

            self.attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1

        # Auto-calculate total points
        self.total_points_earned = self.base_points_earned + self.bonus_points_earned

        # Set max possible score from lab
        if not self.max_possible_score:
            self.max_possible_score = self.lab.max_score

        # Determine if passed and perfect score
        if self.score is not None:
            self.is_passed = self.score >= self.lab.min_score
            self.is_perfect_score = self.score >= self.max_possible_score

        # Set cooldown
        if self.ended_at and not self.cooldown_until and self.lab.cooldown_minutes > 0:
            self.cooldown_until = self.ended_at + timedelta(minutes=self.lab.cooldown_minutes)

        super().save(*args, **kwargs)

        # Award points to user if this is a new passing attempt
        if self.is_passed and self.total_points_earned > 0 and self.pk:
            # Check if this is the first time saving with points
            old_instance = UserLab.objects.filter(pk=self.pk).first()
            if not old_instance or old_instance.total_points_earned == 0:
                self.award_points_to_user()

    def award_points_to_user(self):
        """Award points to user for this lab attempt"""
        if not self.is_passed or self.total_points_earned <= 0:
            return

        # Calculate points
        points_to_award = self.lab.base_points
        description = f"Completed lab: {self.lab.name}"

        # Add bonus for perfect score
        if self.is_perfect_score and self.lab.perfect_score_bonus > 0:
            points_to_award += self.lab.perfect_score_bonus
            description += " (Perfect Score!)"

        # Add any additional bonus points
        if self.lab.bonus_points > 0:
            points_to_award += self.lab.bonus_points

        # Award points to user
        self.user.add_points(
            amount=points_to_award,
            source='lab_completion',
            description=description,
            related_object_id=self.id,
            related_object_type='UserLab'
        )

        # Update the earned points in this record
        self.base_points_earned = self.lab.base_points
        if self.is_perfect_score:
            self.bonus_points_earned = self.lab.perfect_score_bonus + self.lab.bonus_points
        else:
            self.bonus_points_earned = self.lab.bonus_points

        # Save without triggering this method again
        UserLab.objects.filter(pk=self.pk).update(
            base_points_earned=self.base_points_earned,
            bonus_points_earned=self.bonus_points_earned,
            total_points_earned=self.total_points_earned
        )

    @property
    def duration_minutes(self):
        """Calculate duration in minutes"""
        if self.started_at and self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds() / 60)
        return None

    @property
    def score_percentage(self):
        """Calculate score as percentage"""
        if self.score is not None and self.max_possible_score > 0:
            return round((self.score / self.max_possible_score) * 100, 1)
        return None

    def generate_redirect_token(self):
        """Generate secure token for lab redirection"""
        import secrets
        self.redirect_token = secrets.token_urlsafe(32)
        self.save(update_fields=['redirect_token'])
        return self.redirect_token


class LabRedirectSession(models.Model):
    """Secure session management for lab redirections"""

    user_lab = models.OneToOneField(UserLab, on_delete=models.CASCADE, related_name='redirect_session')
    session_token = models.CharField(max_length=255, unique=True)
    redirect_url = models.URLField(help_text="Full URL to redirect user to external lab")
    return_url = models.URLField(help_text="URL where external lab should redirect back")

    # Security
    expires_at = models.DateTimeField(help_text="When this session expires")
    is_used = models.BooleanField(default=False, help_text="Whether this session has been used")
    ip_address = models.GenericIPAddressField(help_text="IP address that initiated the session")
    user_agent = models.TextField(help_text="User agent that initiated the session")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Redirect session for {self.user_lab}"

    def is_valid(self):
        """Check if session is still valid"""
        return not self.is_used and self.expires_at > timezone.now()

    def mark_used(self):
        """Mark session as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.lab}"
