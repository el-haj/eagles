from django.contrib import admin
from django.utils import timezone
from .models import JobCategory, Job, JobApplication, JobView, JobPost

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_count', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'created_at')
    prepopulated_fields = {'name': ('name',)}

    def job_count(self, obj):
        return obj.jobs.count()
    job_count.short_description = 'Jobs'

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company_name', 'job_type', 'status', 'application_count',
        'is_featured', 'is_urgent', 'application_deadline', 'created_at'
    )
    list_filter = (
        'status', 'job_type', 'employment_type', 'experience_level',
        'is_remote', 'remote_type', 'is_featured', 'is_urgent', 'category'
    )
    search_fields = ('title', 'company_name', 'description', 'tags')
    readonly_fields = ('application_count', 'view_count', 'created_at', 'updated_at', 'published_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'requirements', 'responsibilities', 'benefits')
        }),
        ('Job Classification', {
            'fields': ('job_type', 'employment_type', 'experience_level', 'category', 'tags')
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_description', 'company_website', 'company_logo', 'company_size')
        }),
        ('Location & Remote', {
            'fields': ('location', 'is_remote', 'remote_type')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'salary_period')
        }),
        ('Application Details', {
            'fields': ('application_deadline', 'contact_email', 'contact_phone', 'external_url', 'application_instructions')
        }),
        ('Management', {
            'fields': ('posted_by', 'status', 'is_featured', 'is_urgent')
        }),
        ('Statistics & Timestamps', {
            'fields': ('application_count', 'view_count', 'created_at', 'updated_at', 'published_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_featured', 'mark_as_urgent', 'publish_jobs', 'close_jobs']

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} jobs marked as featured.")
    mark_as_featured.short_description = "Mark selected jobs as featured"

    def mark_as_urgent(self, request, queryset):
        queryset.update(is_urgent=True)
        self.message_user(request, f"{queryset.count()} jobs marked as urgent.")
    mark_as_urgent.short_description = "Mark selected jobs as urgent"

    def publish_jobs(self, request, queryset):
        count = queryset.filter(status='draft').update(status='published', published_at=timezone.now())
        self.message_user(request, f"{count} jobs published.")
    publish_jobs.short_description = "Publish selected draft jobs"

    def close_jobs(self, request, queryset):
        count = queryset.filter(status='published').update(status='closed', closed_at=timezone.now())
        self.message_user(request, f"{count} jobs closed.")
    close_jobs.short_description = "Close selected published jobs"

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'applicant_name', 'job_title', 'status', 'rating', 'days_since_applied', 'created_at'
    )
    list_filter = ('status', 'rating', 'job__job_type', 'job__category', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'job__title', 'job__company_name')
    readonly_fields = ('applicant_profile', 'created_at', 'updated_at', 'days_since_applied')

    fieldsets = (
        ('Application Info', {
            'fields': ('user', 'job', 'status', 'rating')
        }),
        ('Application Content', {
            'fields': ('cover_letter', 'resume_file', 'portfolio_links')
        }),
        ('Management', {
            'fields': ('admin_notes', 'last_contact_date', 'interview_date', 'interview_notes')
        }),
        ('Profile Snapshot', {
            'fields': ('applicant_profile',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'reviewed_at', 'days_since_applied'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_reviewing', 'mark_as_shortlisted', 'mark_as_rejected']

    def applicant_name(self, obj):
        return obj.applicant_name
    applicant_name.short_description = 'Applicant'

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'

    def mark_as_reviewing(self, request, queryset):
        queryset.update(status='reviewing')
        self.message_user(request, f"{queryset.count()} applications marked as under review.")
    mark_as_reviewing.short_description = "Mark as under review"

    def mark_as_shortlisted(self, request, queryset):
        queryset.update(status='shortlisted')
        self.message_user(request, f"{queryset.count()} applications shortlisted.")
    mark_as_shortlisted.short_description = "Mark as shortlisted"

    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} applications rejected.")
    mark_as_rejected.short_description = "Mark as rejected"

@admin.register(JobView)
class JobViewAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at', 'job__category')
    search_fields = ('job__title', 'user__username', 'ip_address')
    readonly_fields = ('job', 'user', 'ip_address', 'user_agent', 'viewed_at')

    def has_add_permission(self, request):
        return False  # Views are created automatically

# Keep legacy JobPost admin for backward compatibility
@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'status', 'created_at')
    search_fields = ('user__username', 'job__title')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)
