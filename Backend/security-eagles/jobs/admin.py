from django.contrib import admin
from .models import Job, JobPost

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'category', 'is_remote', 'application_deadline', 'created_at')
    search_fields = ('title', 'company_name', 'category')
    list_filter = ('is_remote', 'category', 'job_type', 'experience_level')

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    search_fields = ('user__username', 'job__title')
    list_filter = ('created_at',)
