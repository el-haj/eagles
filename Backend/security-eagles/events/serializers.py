# events/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Event, EventImage, EventCategory, EventRegistration

class EventCategorySerializer(serializers.ModelSerializer):
    event_count = serializers.ReadOnlyField()

    class Meta:
        model = EventCategory
        fields = ['id', 'name', 'slug', 'description', 'color', 'icon', 'event_count']

class EventImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = EventImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'caption', 'is_featured', 'order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class EventPreviewSerializer(serializers.ModelSerializer):
    """Serializer for event listings/previews"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    status_display = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    is_passed = serializers.ReadOnlyField()
    registration_open = serializers.ReadOnlyField()
    attendee_count = serializers.ReadOnlyField()
    spots_remaining = serializers.ReadOnlyField()
    duration_hours = serializers.ReadOnlyField()
    featured_image = serializers.SerializerMethodField()
    organizer_name = serializers.CharField(source='organizer', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'subtitle', 'description', 'objectives',
            'category_name', 'category_color', 'event_type', 'tags',
            'status', 'status_display', 'priority', 'is_featured',
            'is_physical', 'location', 'platforms', 'platform_urls',
            'start_time', 'end_time', 'timezone_info', 'duration_hours',
            'is_recurring', 'recurrence_type',
            'max_attendees', 'registration_required', 'registration_deadline',
            'registration_url', 'attendee_count', 'spots_remaining', 'registration_open',
            'organizer_name', 'organizer_email', 'organizer_website',
            'is_upcoming', 'is_ongoing', 'is_passed',
            'views', 'featured_image', 'created_by_name', 'published_at', 'created_at'
        ]

    def get_featured_image(self, obj):
        featured_image = obj.images.filter(is_featured=True).first()
        if not featured_image:
            featured_image = obj.images.first()

        if featured_image:
            return EventImageSerializer(featured_image, context=self.context).data
        return None

class EventDetailSerializer(serializers.ModelSerializer):
    """Serializer for full event details"""
    category = EventCategorySerializer(read_only=True)
    images = EventImageSerializer(many=True, read_only=True)
    status_display = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    is_passed = serializers.ReadOnlyField()
    registration_open = serializers.ReadOnlyField()
    attendee_count = serializers.ReadOnlyField()
    spots_remaining = serializers.ReadOnlyField()
    duration_hours = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    view_count_today = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'subtitle', 'description', 'long_description', 'objectives',
            'category', 'event_type', 'tags', 'status', 'status_display', 'priority', 'is_featured',
            'is_physical', 'location', 'address', 'platforms', 'platform_urls',
            'start_time', 'end_time', 'timezone_info', 'duration_hours',
            'is_recurring', 'recurrence_type', 'recurrence_interval', 'recurrence_end_date',
            'max_attendees', 'registration_required', 'registration_deadline', 'registration_url',
            'attendee_count', 'spots_remaining', 'registration_open',
            'organizer', 'organizer_email', 'organizer_phone', 'organizer_website',
            'is_upcoming', 'is_ongoing', 'is_passed',
            'meta_description', 'meta_keywords',
            'views', 'view_count_today', 'images', 'created_by_name',
            'published_at', 'created_at', 'updated_at'
        ]

    def get_view_count_today(self, obj):
        from datetime import timedelta
        today = timezone.now().date()
        return obj.view_records.filter(created_at__date=today).count()

class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating events"""

    class Meta:
        model = Event
        fields = [
            'title', 'subtitle', 'description', 'long_description', 'objectives',
            'category', 'event_type', 'tags', 'status', 'priority', 'is_featured',
            'is_physical', 'location', 'address', 'platforms', 'platform_urls',
            'start_time', 'end_time', 'timezone_info',
            'is_recurring', 'recurrence_type', 'recurrence_interval', 'recurrence_end_date',
            'max_attendees', 'registration_required', 'registration_deadline', 'registration_url',
            'organizer', 'organizer_email', 'organizer_phone', 'organizer_website',
            'meta_description', 'meta_keywords', 'admin_notes'
        ]

    def validate(self, data):
        """Validate event data"""
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("End time must be after start time")

        if data.get('registration_deadline') and data.get('start_time'):
            if data['registration_deadline'] >= data['start_time']:
                raise serializers.ValidationError("Registration deadline must be before event start time")

        if data.get('is_physical') and not data.get('location'):
            raise serializers.ValidationError("Location is required for physical events")

        if not data.get('is_physical') and not data.get('platforms'):
            raise serializers.ValidationError("At least one platform is required for online events")

        return data

class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for event registrations"""
    event_title = serializers.CharField(source='event.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'event_title', 'user_name', 'is_canceled',
                 'registration_data', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['user']
