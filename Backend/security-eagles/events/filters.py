# events/filters.py
import django_filters
from django.utils import timezone
from .models import Event, EventCategory

class EventFilter(django_filters.FilterSet):
    """Filter for events with various criteria"""
    
    # Category filtering
    category = django_filters.ModelChoiceFilter(
        queryset=EventCategory.objects.filter(is_active=True),
        field_name='category'
    )
    category_slug = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='iexact'
    )
    
    # Event type filtering
    event_type = django_filters.ChoiceFilter(
        choices=Event.EVENT_TYPE_CHOICES
    )
    
    # Status filtering
    status = django_filters.ChoiceFilter(
        choices=Event.STATUS_CHOICES
    )
    
    # Priority filtering
    priority = django_filters.ChoiceFilter(
        choices=Event.PRIORITY_CHOICES
    )
    
    # Location type filtering
    is_physical = django_filters.BooleanFilter()
    
    # Featured events
    is_featured = django_filters.BooleanFilter()
    
    # Recurring events
    is_recurring = django_filters.BooleanFilter()
    
    # Registration filtering
    registration_required = django_filters.BooleanFilter()
    registration_open = django_filters.BooleanFilter(
        method='filter_registration_open'
    )
    
    # Date range filtering
    start_date = django_filters.DateTimeFilter(
        field_name='start_time',
        lookup_expr='gte'
    )
    end_date = django_filters.DateTimeFilter(
        field_name='end_time',
        lookup_expr='lte'
    )
    
    # Time-based filters
    upcoming = django_filters.BooleanFilter(
        method='filter_upcoming'
    )
    ongoing = django_filters.BooleanFilter(
        method='filter_ongoing'
    )
    past = django_filters.BooleanFilter(
        method='filter_past'
    )
    
    # This week/month filters
    this_week = django_filters.BooleanFilter(
        method='filter_this_week'
    )
    this_month = django_filters.BooleanFilter(
        method='filter_this_month'
    )
    
    # Tags filtering
    tags = django_filters.CharFilter(
        method='filter_tags'
    )
    
    # Organizer filtering
    organizer = django_filters.CharFilter(
        lookup_expr='icontains'
    )
    
    # Platform filtering
    platform = django_filters.CharFilter(
        method='filter_platform'
    )

    class Meta:
        model = Event
        fields = [
            'category', 'category_slug', 'event_type', 'status', 'priority',
            'is_physical', 'is_featured', 'is_recurring', 'registration_required',
            'start_date', 'end_date', 'upcoming', 'ongoing', 'past',
            'this_week', 'this_month', 'tags', 'organizer', 'platform'
        ]

    def filter_registration_open(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                registration_required=True,
                registration_deadline__gt=now,
                start_time__gt=now
            )
        return queryset

    def filter_upcoming(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(start_time__gt=now)
        return queryset

    def filter_ongoing(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                start_time__lte=now,
                end_time__gte=now
            )
        return queryset

    def filter_past(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(end_time__lt=now)
        return queryset

    def filter_this_week(self, queryset, name, value):
        if value:
            now = timezone.now()
            start_of_week = now - timezone.timedelta(days=now.weekday())
            end_of_week = start_of_week + timezone.timedelta(days=6)
            return queryset.filter(
                start_time__gte=start_of_week,
                start_time__lte=end_of_week
            )
        return queryset

    def filter_this_month(self, queryset, name, value):
        if value:
            now = timezone.now()
            start_of_month = now.replace(day=1)
            if now.month == 12:
                end_of_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                end_of_month = now.replace(month=now.month + 1, day=1)
            return queryset.filter(
                start_time__gte=start_of_month,
                start_time__lt=end_of_month
            )
        return queryset

    def filter_tags(self, queryset, name, value):
        if value:
            tags = [tag.strip() for tag in value.split(',')]
            return queryset.filter(tags__overlap=tags)
        return queryset

    def filter_platform(self, queryset, name, value):
        if value:
            return queryset.filter(platforms__icontains=value)
        return queryset
