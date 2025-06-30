# events/admin.py
from django.contrib import admin
from .models import Event, EventImage
from django.utils.html import format_html

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'start_time', 'end_time', 'is_active', 'created_by', 'created_at']
    inlines = [EventImageInline]
