# events/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Event, EventImage, EventCategory, EventRegistration, EventView

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1
    readonly_fields = ['image_preview']
    fields = ['image', 'image_preview', 'alt_text', 'caption', 'is_featured', 'order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'event_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['event_count']

    def event_count(self, obj):
        return obj.event_count
    event_count.short_description = "Events"

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status', 'status_badge', 'event_type', 'category',
        'start_time', 'is_featured', 'views', 'attendee_count', 'created_by'
    ]
    list_filter = [
        'status', 'event_type', 'category', 'priority', 'is_featured',
        'is_physical', 'is_recurring', 'registration_required', 'created_at'
    ]
    search_fields = ['title', 'description', 'organizer', 'tags']
    readonly_fields = [
        'slug', 'views', 'attendee_count', 'status_display', 'is_upcoming',
        'is_ongoing', 'is_passed', 'registration_open', 'spots_remaining',
        'duration_hours', 'created_at', 'updated_at', 'published_at'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'subtitle', 'description', 'long_description', 'objectives'
            )
        }),
        ('Categorization', {
            'fields': ('category', 'event_type', 'tags', 'status', 'priority', 'is_featured')
        }),
        ('Location & Platform', {
            'fields': (
                'is_physical', 'location', 'address', 'platforms', 'platform_urls'
            )
        }),
        ('Timing', {
            'fields': (
                'start_time', 'end_time', 'timezone_info', 'duration_hours',
                'is_recurring', 'recurrence_type', 'recurrence_interval', 'recurrence_end_date'
            )
        }),
        ('Registration', {
            'fields': (
                'max_attendees', 'registration_required', 'registration_deadline',
                'registration_url', 'attendee_count', 'registration_open', 'spots_remaining'
            )
        }),
        ('Organizer Information', {
            'fields': ('organizer', 'organizer_email', 'organizer_phone', 'organizer_website')
        }),
        ('SEO & Meta', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Admin Features', {
            'fields': ('in_lights_date', 'admin_notes', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Status & Tracking', {
            'fields': (
                'slug', 'status_display', 'is_upcoming', 'is_ongoing', 'is_passed',
                'views', 'created_by', 'created_at', 'updated_at', 'published_at'
            ),
            'classes': ('collapse',)
        })
    )

    inlines = [EventImageInline]

    actions = ['publish_events', 'archive_events', 'feature_events', 'unfeature_events']

    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'review': '#ffc107',
            'published': '#28a745',
            'cancelled': '#dc3545',
            'archived': '#6f42c1'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def attendee_count(self, obj):
        return obj.attendee_count
    attendee_count.short_description = "Attendees"

    def publish_events(self, request, queryset):
        updated = queryset.filter(status__in=['draft', 'review']).update(
            status='published',
            published_at=timezone.now()
        )
        self.message_user(request, f'{updated} events published successfully.')
    publish_events.short_description = "Publish selected events"

    def archive_events(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} events archived successfully.')
    archive_events.short_description = "Archive selected events"

    def feature_events(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} events featured successfully.')
    feature_events.short_description = "Feature selected events"

    def unfeature_events(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} events unfeatured successfully.')
    unfeature_events.short_description = "Unfeature selected events"

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'is_canceled', 'created_at']
    list_filter = ['is_canceled', 'created_at', 'event__category']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(EventView)
class EventViewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['event__title', 'user__username', 'ip_address']
    readonly_fields = ['created_at']
