
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



class User(AbstractUser):

    sso_provider = models.CharField(max_length=255, blank=True, null=True)
    sso_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    score = models.IntegerField(default=0)

    # Points System
    total_points = models.IntegerField(default=0, help_text="Total points earned by user")
    available_points = models.IntegerField(default=0, help_text="Points available to spend")

    cv = models.FileField(upload_to='user_cvs/', blank=True, null=True)
    profile_pic = models.ImageField(upload_to='user_pics/', blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=20, choices=[('public', 'Public'), ('private', 'Private')], default='public')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    meta_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser

    def add_points(self, amount, source, description="", related_object_id=None, related_object_type=None):
        """Add points to user account and create transaction record"""
        if amount <= 0:
            return False

        self.total_points += amount
        self.available_points += amount
        self.save()

        # Create transaction record
        PointsTransaction.objects.create(
            user=self,
            transaction_type='earned',
            amount=amount,
            source=source,
            description=description,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            balance_after=self.available_points
        )
        return True

    def spend_points(self, amount, purpose, description="", related_object_id=None, related_object_type=None):
        """Spend points from user account and create transaction record"""
        if amount <= 0 or self.available_points < amount:
            return False

        self.available_points -= amount
        self.save()

        # Create transaction record
        PointsTransaction.objects.create(
            user=self,
            transaction_type='spent',
            amount=amount,
            source=purpose,
            description=description,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            balance_after=self.available_points
        )
        return True


class PointsTransaction(models.Model):
    """Track all points transactions for users"""

    TRANSACTION_TYPES = [
        ('earned', 'Points Earned'),
        ('spent', 'Points Spent'),
        ('bonus', 'Bonus Points'),
        ('penalty', 'Points Penalty'),
        ('refund', 'Points Refund'),
        ('admin_adjustment', 'Admin Adjustment'),
    ]

    POINT_SOURCES = [
        ('lab_completion', 'Lab Completion'),
        ('lab_perfect_score', 'Lab Perfect Score'),
        ('daily_login', 'Daily Login'),
        ('profile_completion', 'Profile Completion'),
        ('referral', 'User Referral'),
        ('event_participation', 'Event Participation'),
        ('community_contribution', 'Community Contribution'),
        ('achievement_unlock', 'Achievement Unlock'),
        ('store_purchase', 'Store Purchase'),
        ('premium_feature', 'Premium Feature'),
        ('certification', 'Certification'),
        ('admin_reward', 'Admin Reward'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField(help_text="Points amount (positive for earned, negative for spent)")
    source = models.CharField(max_length=30, choices=POINT_SOURCES)
    description = models.TextField(blank=True, help_text="Additional details about the transaction")

    # Optional reference to related object
    related_object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object_type = models.CharField(max_length=50, blank=True, null=True, help_text="Model name of related object")

    # Transaction metadata
    balance_after = models.IntegerField(help_text="User's available points balance after this transaction")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_transactions')

    # Admin fields
    is_reversed = models.BooleanField(default=False, help_text="Whether this transaction has been reversed")
    reversed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reversed_transactions')
    reversed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
            models.Index(fields=['source', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} {self.amount} points"


class PointsReward(models.Model):
    """Define point rewards for different activities"""

    activity_type = models.CharField(max_length=30, choices=PointsTransaction.POINT_SOURCES, unique=True)
    points_amount = models.IntegerField(help_text="Points to award for this activity")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    # Conditions
    max_per_day = models.IntegerField(null=True, blank=True, help_text="Maximum times per day this reward can be earned")
    max_per_week = models.IntegerField(null=True, blank=True, help_text="Maximum times per week this reward can be earned")
    max_total = models.IntegerField(null=True, blank=True, help_text="Maximum total times this reward can be earned")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['activity_type']

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.points_amount} points"
