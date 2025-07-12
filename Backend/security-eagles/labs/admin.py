from django.contrib import admin
from .models import Lab, UserLab, LabRedirectSession

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'difficulty_level', 'status', 'estimated_time', 'base_points', 'created_at')
    search_fields = ('name', 'category', 'difficulty_level', 'external_lab_id')
    list_filter = ('category', 'difficulty_level', 'status', 'is_featured')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'objectives', 'category', 'difficulty_level', 'status')
        }),
        ('Lab Configuration', {
            'fields': ('lab_url', 'external_lab_id', 'estimated_time')
        }),
        ('Scoring & Points', {
            'fields': ('max_score', 'min_score', 'perfect_score_bonus', 'base_points', 'bonus_points')
        }),
        ('Access Control', {
            'fields': ('cooldown_minutes', 'max_attempts_per_day', 'requires_prerequisites', 'prerequisite_labs')
        }),
        ('Metadata', {
            'fields': ('tags', 'notes', 'is_featured', 'created_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(UserLab)
class UserLabAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lab', 'attempt_number', 'status', 'score', 'is_passed', 'total_points_earned', 'started_at')
    search_fields = ('user__username', 'lab__name', 'external_attempt_id')
    list_filter = ('status', 'is_passed', 'is_perfect_score', 'lab__category', 'lab__difficulty_level')
    ordering = ('-created_at',)
    readonly_fields = ('attempt_number', 'is_passed', 'is_perfect_score', 'total_points_earned', 'duration_minutes', 'score_percentage', 'created_at', 'updated_at')

    fieldsets = (
        ('Attempt Information', {
            'fields': ('user', 'lab', 'attempt_number', 'status', 'started_at', 'ended_at', 'time_spent')
        }),
        ('Results', {
            'fields': ('score', 'max_possible_score', 'is_passed', 'is_perfect_score', 'duration_minutes', 'score_percentage')
        }),
        ('Points & Rewards', {
            'fields': ('base_points_earned', 'bonus_points_earned', 'total_points_earned')
        }),
        ('External Integration', {
            'fields': ('external_attempt_id', 'external_session_token', 'redirect_token')
        }),
        ('Metadata', {
            'fields': ('cooldown_until', 'ip_address', 'user_agent', 'notes', 'created_at', 'updated_at')
        }),
    )

@admin.register(LabRedirectSession)
class LabRedirectSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_lab', 'session_token', 'expires_at', 'is_used', 'created_at')
    search_fields = ('session_token', 'user_lab__user__username', 'user_lab__lab__name')
    list_filter = ('is_used', 'expires_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'used_at')
