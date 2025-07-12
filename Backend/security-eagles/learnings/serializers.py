from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Track, LearningPath, LearningSection, UserLearningProgress,
    LearningComment, LearningRating
)

User = get_user_model()


class TrackSerializer(serializers.ModelSerializer):
    """Serializer for Track model - no auth required"""
    thumbnail_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = Track
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'level', 'level_display', 'thumbnail_url', 'pdf_url', 'tags',
            'duration_hours', 'prerequisites', 'download_count', 'created_at'
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    def get_pdf_url(self, obj):
        if obj.pdf_file and hasattr(obj.pdf_file, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None


class LearningPathListSerializer(serializers.ModelSerializer):
    """Serializer for learning path list view"""
    thumbnail_url = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    sections_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = [
            'id', 'title', 'short_description', 'category', 'category_display',
            'level', 'level_display', 'thumbnail_url', 'estimated_duration_hours',
            'instructor_name', 'sections_count', 'enrollment_count', 'average_rating',
            'total_ratings', 'is_featured', 'is_enrolled', 'user_progress', 'created_at'
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    def get_sections_count(self, obj):
        return obj.sections.filter(is_active=True).count()

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserLearningProgress.objects.filter(
                user=request.user, learning_path=obj
            ).exists()
        return False

    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserLearningProgress.objects.get(
                    user=request.user, learning_path=obj
                )
                return {
                    'status': progress.status,
                    'progress_percentage': float(progress.progress_percentage),
                    'last_accessed_at': progress.last_accessed_at
                }
            except UserLearningProgress.DoesNotExist:
                pass
        return None


class LearningSectionSerializer(serializers.ModelSerializer):
    """Serializer for learning sections"""
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    pdf_url = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = LearningSection
        fields = [
            'id', 'title', 'description', 'order', 'content_type', 'content_type_display',
            'video_url', 'pdf_url', 'markdown_content', 'estimated_duration_minutes',
            'is_required', 'is_completed'
        ]

    def get_pdf_url(self, obj):
        if obj.pdf_file and hasattr(obj.pdf_file, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserLearningProgress.objects.get(
                    user=request.user, learning_path=obj.learning_path
                )
                return obj in progress.completed_sections.all()
            except UserLearningProgress.DoesNotExist:
                pass
        return False


class LearningPathDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for learning path with sections"""
    thumbnail_url = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    sections = LearningSectionSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = [
            'id', 'title', 'description', 'short_description', 'category', 'category_display',
            'level', 'level_display', 'thumbnail_url', 'intro_video_url',
            'estimated_duration_hours', 'prerequisites', 'learning_objectives', 'tags',
            'instructor_name', 'enrollment_count', 'completion_count', 'average_rating',
            'total_ratings', 'is_featured', 'sections', 'is_enrolled', 'user_progress',
            'user_rating', 'created_at', 'published_at'
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserLearningProgress.objects.filter(
                user=request.user, learning_path=obj
            ).exists()
        return False

    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserLearningProgress.objects.get(
                    user=request.user, learning_path=obj
                )
                return {
                    'status': progress.status,
                    'progress_percentage': float(progress.progress_percentage),
                    'current_section_id': progress.current_section.id if progress.current_section else None,
                    'completed_sections_count': progress.completed_sections.count(),
                    'enrolled_at': progress.enrolled_at,
                    'started_at': progress.started_at,
                    'completed_at': progress.completed_at,
                    'last_accessed_at': progress.last_accessed_at
                }
            except UserLearningProgress.DoesNotExist:
                pass
        return None

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = LearningRating.objects.get(
                    user=request.user, learning_path=obj
                )
                return {
                    'rating': rating.rating,
                    'review': rating.review,
                    'created_at': rating.created_at
                }
            except LearningRating.DoesNotExist:
                pass
        return None


class UserLearningProgressSerializer(serializers.ModelSerializer):
    """Serializer for user learning progress"""
    learning_path = LearningPathListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    completed_sections_count = serializers.SerializerMethodField()
    total_sections_count = serializers.SerializerMethodField()

    class Meta:
        model = UserLearningProgress
        fields = [
            'id', 'learning_path', 'status', 'status_display', 'progress_percentage',
            'completed_sections_count', 'total_sections_count', 'enrolled_at',
            'started_at', 'completed_at', 'last_accessed_at'
        ]

    def get_completed_sections_count(self, obj):
        return obj.completed_sections.count()

    def get_total_sections_count(self, obj):
        return obj.learning_path.sections.filter(is_active=True, is_required=True).count()


class LearningCommentSerializer(serializers.ModelSerializer):
    """Serializer for learning comments"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    replies_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = LearningComment
        fields = [
            'id', 'content', 'user_name', 'user_username', 'parent', 'replies_count',
            'is_edited', 'is_owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'is_edited']

    def get_replies_count(self, obj):
        return obj.replies.filter(is_active=True).count()

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False


class LearningRatingSerializer(serializers.ModelSerializer):
    """Serializer for learning ratings"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = LearningRating
        fields = [
            'id', 'rating', 'review', 'user_name', 'user_username',
            'is_owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False
