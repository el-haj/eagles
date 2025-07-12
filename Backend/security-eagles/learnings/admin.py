from django.contrib import admin
from .models import (
    Track, LearningPath, LearningSection, UserLearningProgress,
    LearningComment, LearningRating
)


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'level', 'duration_hours', 'download_count', 'is_active', 'created_at']
    list_filter = ['category', 'level', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['download_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'level')
        }),
        ('Content', {
            'fields': ('pdf_file', 'thumbnail', 'tags')
        }),
        ('Learning Details', {
            'fields': ('duration_hours', 'prerequisites')
        }),
        ('Status & Statistics', {
            'fields': ('is_active', 'download_count', 'created_at', 'updated_at')
        }),
    )


class LearningSectionInline(admin.TabularInline):
    model = LearningSection
    extra = 0
    fields = ['title', 'order', 'content_type', 'estimated_duration_minutes', 'is_required', 'is_active']
    ordering = ['order']


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['title', 'track', 'category', 'level', 'instructor', 'status', 'enrollment_count', 'average_rating', 'is_featured']
    list_filter = ['track', 'category', 'level', 'status', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['enrollment_count', 'completion_count', 'average_rating', 'total_ratings', 'created_at', 'updated_at', 'published_at']
    inlines = [LearningSectionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('track', 'title', 'description', 'short_description', 'category', 'level')
        }),
        ('Media', {
            'fields': ('thumbnail', 'intro_video_url')
        }),
        ('Learning Details', {
            'fields': ('estimated_duration_hours', 'prerequisites', 'learning_objectives', 'tags')
        }),
        ('Management', {
            'fields': ('instructor', 'status', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('enrollment_count', 'completion_count', 'average_rating', 'total_ratings')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at')
        }),
    )


@admin.register(LearningSection)
class LearningSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'learning_path', 'order', 'content_type', 'estimated_duration_minutes', 'is_required', 'is_active']
    list_filter = ['content_type', 'is_required', 'is_active', 'learning_path__category']
    search_fields = ['title', 'description', 'learning_path__title']
    ordering = ['learning_path', 'order']


@admin.register(UserLearningProgress)
class UserLearningProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'learning_path', 'status', 'progress_percentage', 'enrolled_at', 'last_accessed_at']
    list_filter = ['status', 'learning_path__category', 'enrolled_at']
    search_fields = ['user__username', 'user__email', 'learning_path__title']
    readonly_fields = ['progress_percentage', 'enrolled_at', 'started_at', 'completed_at', 'last_accessed_at']


@admin.register(LearningComment)
class LearningCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'section', 'content_preview', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'section__learning_path__category', 'created_at']
    search_fields = ['user__username', 'section__title', 'content']
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(LearningRating)
class LearningRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'learning_path', 'rating', 'review_preview', 'created_at']
    list_filter = ['rating', 'learning_path__category', 'created_at']
    search_fields = ['user__username', 'learning_path__title', 'review']
    readonly_fields = ['created_at', 'updated_at']

    def review_preview(self, obj):
        if obj.review:
            return obj.review[:50] + '...' if len(obj.review) > 50 else obj.review
        return 'No review'
    review_preview.short_description = 'Review Preview'
