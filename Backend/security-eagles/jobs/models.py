from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

class JobCategory(models.Model):
    """Job categories for better organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Job Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Job(models.Model):
    # Job Type Choices
    JOB_TYPE_CHOICES = [
        ('job', 'Job'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('contract', 'Contract'),
    ]

    # Employment Type Choices
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full-Time'),
        ('part_time', 'Part-Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('volunteer', 'Volunteer'),
    ]

    # Experience Level Choices
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('executive', 'Executive'),
    ]

    # Status Choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('filled', 'Filled'),
    ]

    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()
    benefits = models.TextField(blank=True, help_text="Benefits and perks offered")

    # Job Classification
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='job')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='mid')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list, help_text="Skills and technologies")

    # Company Information
    company_name = models.CharField(max_length=255)
    company_description = models.TextField(blank=True, help_text="About the company")
    company_website = models.URLField(blank=True, null=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    company_size = models.CharField(max_length=50, blank=True, help_text="e.g., 1-10, 11-50, 51-200, 200+")

    # Location and Remote
    location = models.CharField(max_length=255, help_text="City, State/Country")
    is_remote = models.BooleanField(default=False)
    remote_type = models.CharField(max_length=20, choices=[
        ('fully_remote', 'Fully Remote'),
        ('hybrid', 'Hybrid'),
        ('on_site', 'On-Site'),
    ], default='on_site')

    # Compensation
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    salary_period = models.CharField(max_length=20, choices=[
        ('hourly', 'Per Hour'),
        ('daily', 'Per Day'),
        ('weekly', 'Per Week'),
        ('monthly', 'Per Month'),
        ('yearly', 'Per Year'),
    ], default='yearly')

    # Application Details
    application_deadline = models.DateTimeField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True, help_text="External job posting URL")
    application_instructions = models.TextField(blank=True, help_text="Special instructions for applicants")

    # Management
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False, help_text="Featured jobs appear at the top")
    is_urgent = models.BooleanField(default=False, help_text="Urgent jobs get special highlighting")

    # Statistics
    application_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-is_featured', '-is_urgent', '-created_at']
        indexes = [
            models.Index(fields=['status', 'job_type']),
            models.Index(fields=['category', 'experience_level']),
            models.Index(fields=['is_remote', 'location']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company_name}"

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if job is currently active for applications"""
        return (
            self.status == 'published' and
            timezone.now() < self.application_deadline and
            not self.closed_at
        )

    @property
    def days_until_deadline(self):
        """Days remaining until application deadline"""
        if not self.application_deadline:
            return None
        delta = self.application_deadline - timezone.now()
        return max(0, delta.days)

    @property
    def salary_range_display(self):
        """Human readable salary range"""
        if not self.salary_min and not self.salary_max:
            return "Salary not specified"

        currency_symbol = {'USD': '$', 'EUR': '€', 'GBP': '£'}.get(self.salary_currency, self.salary_currency)

        if self.salary_min and self.salary_max:
            return f"{currency_symbol}{self.salary_min:,.0f} - {currency_symbol}{self.salary_max:,.0f} {self.get_salary_period_display()}"
        elif self.salary_min:
            return f"From {currency_symbol}{self.salary_min:,.0f} {self.get_salary_period_display()}"
        elif self.salary_max:
            return f"Up to {currency_symbol}{self.salary_max:,.0f} {self.get_salary_period_display()}"

class JobApplication(models.Model):
    """Job applications submitted by users"""

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewing', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_completed', 'Interview Completed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn by Applicant'),
    ]

    # Core Application Data
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')

    # Application Content
    cover_letter = models.TextField(help_text="Cover letter or application message")
    resume_file = models.FileField(upload_to='application_resumes/', blank=True, null=True, help_text="Uploaded resume file")
    portfolio_links = ArrayField(models.URLField(), blank=True, default=list, help_text="Portfolio or work sample links")

    # Auto-filled Profile Data (snapshot at application time)
    applicant_profile = models.JSONField(help_text="Snapshot of user profile at application time")

    # Application Management
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Internal notes from hiring team")
    rating = models.IntegerField(null=True, blank=True, help_text="Rating from 1-5 by hiring team")

    # Communication
    last_contact_date = models.DateTimeField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'job')  # One application per user per job
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} applied to {self.job.title}"

    def save(self, *args, **kwargs):
        # Auto-fill profile data on creation
        if not self.pk and not self.applicant_profile:
            self.applicant_profile = {
                'username': self.user.username,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'phone': self.user.phone,
                'city': self.user.city,
                'github': self.user.github,
                'linkedin': self.user.linkedin,
                'portfolio_url': self.user.portfolio_url,
                'cv_url': self.user.cv.url if self.user.cv else None,
                'profile_pic_url': self.user.profile_pic.url if self.user.profile_pic else None,
                'score': self.user.score,
                'meta_data': self.user.meta_data,
                'applied_at': timezone.now().isoformat(),
            }

        # Set reviewed_at when status changes from pending
        if self.pk:
            old_instance = JobApplication.objects.get(pk=self.pk)
            if old_instance.status == 'pending' and self.status != 'pending' and not self.reviewed_at:
                self.reviewed_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def applicant_name(self):
        """Get applicant's full name"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username

    @property
    def days_since_applied(self):
        """Days since application was submitted"""
        delta = timezone.now() - self.created_at
        return delta.days


class JobView(models.Model):
    """Track job page views for analytics"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='view_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['job', 'viewed_at']),
        ]

    def __str__(self):
        return f"View of {self.job.title} at {self.viewed_at}"


# Keep JobPost for backward compatibility (deprecated)
class JobPost(models.Model):
    """Deprecated: Use JobApplication instead"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_posts')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='legacy_applications')
    message = models.TextField(blank=True, null=True, help_text="Message from applicant to employer")
    meta_data = models.JSONField(blank=True, null=True, help_text="Auto-filled with user bio and other details at apply time")
    status = models.CharField(max_length=50, default='pending', help_text="Application status: pending, accepted, rejected, etc.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} applied to {self.job.title}"
