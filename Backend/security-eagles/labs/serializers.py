from rest_framework import serializers
from django.utils import timezone
from .models import Lab, UserLab, LabRedirectSession


class LabSerializer(serializers.ModelSerializer):
    """Serializer for Lab model with user-specific context"""

    can_attempt = serializers.SerializerMethodField()
    user_attempts_count = serializers.SerializerMethodField()
    user_best_score = serializers.SerializerMethodField()
    user_has_passed = serializers.SerializerMethodField()
    cooldown_remaining = serializers.SerializerMethodField()
    attempts_today = serializers.SerializerMethodField()

    class Meta:
        model = Lab
        fields = [
            'id', 'name', 'description', 'objectives', 'category', 'difficulty_level',
            'status', 'lab_url', 'external_lab_id', 'estimated_time', 'max_score',
            'min_score', 'perfect_score_bonus', 'base_points', 'bonus_points',
            'cooldown_minutes', 'max_attempts_per_day', 'requires_prerequisites',
            'tags', 'notes', 'is_featured', 'created_at', 'updated_at',
            # User-specific fields
            'can_attempt', 'user_attempts_count', 'user_best_score',
            'user_has_passed', 'cooldown_remaining', 'attempts_today'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'external_lab_id']

    def get_can_attempt(self, obj):
        """Check if current user can attempt this lab"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        can_attempt, _ = obj.can_user_attempt(request.user)
        return can_attempt

    def get_user_attempts_count(self, obj):
        """Get number of attempts by current user"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0

        return UserLab.objects.filter(user=request.user, lab=obj).count()

    def get_user_best_score(self, obj):
        """Get user's best score for this lab"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        best_attempt = UserLab.objects.filter(
            user=request.user,
            lab=obj,
            score__isnull=False
        ).order_by('-score').first()

        return best_attempt.score if best_attempt else None

    def get_user_has_passed(self, obj):
        """Check if user has passed this lab"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        return UserLab.objects.filter(
            user=request.user,
            lab=obj,
            is_passed=True
        ).exists()

    def get_cooldown_remaining(self, obj):
        """Get remaining cooldown time in minutes"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0

        return obj.get_user_cooldown_remaining(request.user)

    def get_attempts_today(self, obj):
        """Get number of attempts today"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0

        return obj.get_user_attempts_today(request.user)


class UserLabSerializer(serializers.ModelSerializer):
    """Serializer for UserLab model"""

    lab_name = serializers.CharField(source='lab.name', read_only=True)
    lab_category = serializers.CharField(source='lab.category', read_only=True)
    lab_difficulty = serializers.CharField(source='lab.difficulty_level', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    score_percentage = serializers.ReadOnlyField()

    class Meta:
        model = UserLab
        fields = [
            'id', 'lab', 'lab_name', 'lab_category', 'lab_difficulty',
            'attempt_number', 'status', 'started_at', 'ended_at', 'time_spent',
            'score', 'max_possible_score', 'is_passed', 'is_perfect_score',
            'base_points_earned', 'bonus_points_earned', 'total_points_earned',
            'external_attempt_id', 'cooldown_until', 'notes',
            'duration_minutes', 'score_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'attempt_number', 'is_passed', 'is_perfect_score',
            'base_points_earned', 'bonus_points_earned', 'total_points_earned',
            'cooldown_until', 'duration_minutes', 'score_percentage',
            'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Validate user lab data"""
        if data.get('ended_at') and data.get('started_at'):
            if data['ended_at'] < data['started_at']:
                raise serializers.ValidationError("End time cannot be before start time")

        if data.get('score') is not None:
            lab = data.get('lab')
            if lab and data['score'] > lab.max_score:
                raise serializers.ValidationError(f"Score cannot exceed maximum score of {lab.max_score}")

        return data


class LabRedirectSessionSerializer(serializers.ModelSerializer):
    """Serializer for LabRedirectSession model"""

    class Meta:
        model = LabRedirectSession
        fields = [
            'id', 'session_token', 'redirect_url', 'return_url',
            'expires_at', 'is_used', 'created_at', 'used_at'
        ]
        read_only_fields = ['id', 'created_at', 'used_at']


class LabStatsSerializer(serializers.Serializer):
    """Serializer for lab statistics"""

    total_labs = serializers.IntegerField()
    active_labs = serializers.IntegerField()
    total_attempts = serializers.IntegerField()
    successful_attempts = serializers.IntegerField()
    average_score = serializers.FloatField()
    total_points_awarded = serializers.IntegerField()


class UserLabStatsSerializer(serializers.Serializer):
    """Serializer for user lab statistics"""

    total_attempts = serializers.IntegerField()
    completed_attempts = serializers.IntegerField()
    passed_attempts = serializers.IntegerField()
    perfect_scores = serializers.IntegerField()
    total_points_earned = serializers.IntegerField()
    average_score = serializers.FloatField()
    labs_completed = serializers.IntegerField()
    total_time_spent = serializers.IntegerField()
    recent_attempts = UserLabSerializer(many=True, read_only=True)
