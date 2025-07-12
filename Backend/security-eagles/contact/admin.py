from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import ContactMessage, ContactSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'subject_display', 'status_display',
        'is_read', 'created_at_formatted', 'actions_column'
    ]
    list_filter = [
        'status', 'subject', 'is_read', 'created_at'
    ]
    search_fields = [
        'name', 'email', 'company', 'message'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'ip_address', 'user_agent'
    ]
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'is_read')
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def subject_display(self, obj):
        return obj.get_subject_display()
    subject_display.short_description = 'Subject'

    def status_display(self, obj):
        colors = {
            'new': '#e74c3c',
            'in_progress': '#f39c12',
            'resolved': '#27ae60',
            'closed': '#95a5a6'
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_formatted.short_description = 'Created'
    created_at_formatted.admin_order_field = 'created_at'

    def actions_column(self, obj):
        if not obj.is_read:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">● Unread</span>'
            )
        return format_html(
            '<span style="color: #27ae60;">✓ Read</span>'
        )
    actions_column.short_description = 'Read Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_resolved']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages marked as unread.')
    mark_as_unread.short_description = 'Mark selected messages as unread'

    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f'{updated} messages marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected messages as resolved'


@admin.register(ContactSettings)
class ContactSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'auto_response_enabled', 'admin_notification_enabled', 'updated_at']

    fieldsets = (
        ('Community Information', {
            'fields': ('community_description', 'contact_email', 'availability_info')
        }),
        ('Community Links', {
            'fields': ('website_url', 'discord_server', 'github_url', 'twitter_url', 'linkedin_url', 'youtube_url'),
            'classes': ('collapse',)
        }),
        ('Auto Response Settings', {
            'fields': ('auto_response_enabled', 'auto_response_message')
        }),
        ('Admin Notifications', {
            'fields': ('admin_notification_enabled', 'admin_notification_emails')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        # Only allow one settings instance
        return not ContactSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False
