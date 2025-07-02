from django.contrib import admin
from .models import Lab, UserLab

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'difficulty_level', 'estimated_time', 'created_by', 'created_at')
    search_fields = ('name', 'category', 'difficulty_level')
    list_filter = ('category', 'difficulty_level')
    ordering = ('-created_at',)

@admin.register(UserLab)
class UserLabAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lab', 'score', 'is_ok', 'time_spent', 'started_at', 'ended_at')
    search_fields = ('user__username', 'lab__name')
    list_filter = ('is_ok', 'lab__category')
    ordering = ('-created_at',)
