
# events/views.py
from rest_framework import generics, pagination, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Event, EventCategory, EventRegistration, EventView
from .serializers import (
    EventPreviewSerializer, EventDetailSerializer, EventCreateUpdateSerializer,
    EventCategorySerializer, EventRegistrationSerializer
)
from .filters import EventFilter

class EventPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

class EventCategoryListView(generics.ListAPIView):
    """List all active event categories"""
    queryset = EventCategory.objects.filter(is_active=True)
    serializer_class = EventCategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class EventListView(generics.ListAPIView):
    """List published events with filtering and search"""
    serializer_class = EventPreviewSerializer
    pagination_class = EventPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'long_description', 'organizer', 'tags']
    ordering_fields = ['start_time', 'created_at', 'views', 'priority']
    ordering = ['-start_time']

    def get_queryset(self):
        return Event.objects.filter(
            status='published',
            is_active=True
        ).select_related('category', 'created_by').prefetch_related('images')

class EventDetailView(generics.RetrieveAPIView):
    """Get detailed event information"""
    serializer_class = EventDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        return Event.objects.filter(
            status='published',
            is_active=True
        ).select_related('category', 'created_by').prefetch_related('images', 'view_records')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Track view
        ip_address = self.get_client_ip(request)
        EventView.objects.get_or_create(
            event=instance,
            user=request.user,
            ip_address=ip_address,
            defaults={'user_agent': request.META.get('HTTP_USER_AGENT', '')}
        )

        # Increment view count
        Event.objects.filter(pk=instance.pk).update(views=models.F('views') + 1)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class FeaturedEventsView(generics.ListAPIView):
    """List featured events"""
    serializer_class = EventPreviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(
            status='published',
            is_active=True,
            is_featured=True
        ).select_related('category', 'created_by').prefetch_related('images')[:10]

class UpcomingEventsView(generics.ListAPIView):
    """List upcoming events"""
    serializer_class = EventPreviewSerializer
    pagination_class = EventPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(
            status='published',
            is_active=True,
            start_time__gt=now
        ).select_related('category', 'created_by').prefetch_related('images').order_by('start_time')

class OngoingEventsView(generics.ListAPIView):
    """List currently ongoing events"""
    serializer_class = EventPreviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(
            status='published',
            is_active=True,
            start_time__lte=now,
            end_time__gte=now
        ).select_related('category', 'created_by').prefetch_related('images').order_by('start_time')

class PastEventsView(generics.ListAPIView):
    """List past events"""
    serializer_class = EventPreviewSerializer
    pagination_class = EventPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(
            status='published',
            is_active=True,
            end_time__lt=now
        ).select_related('category', 'created_by').prefetch_related('images').order_by('-end_time')

class EventSearchView(generics.ListAPIView):
    """Search events"""
    serializer_class = EventPreviewSerializer
    pagination_class = EventPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'long_description', 'organizer', 'tags']

    def get_queryset(self):
        return Event.objects.filter(
            status='published',
            is_active=True
        ).select_related('category', 'created_by').prefetch_related('images')

# ADMIN VIEWS (Staff/Admin Only)
class EventAdminListView(generics.ListCreateAPIView):
    """Admin view for listing and creating events"""
    serializer_class = EventPreviewSerializer
    pagination_class = EventPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'long_description', 'organizer', 'tags']
    ordering_fields = ['start_time', 'created_at', 'views', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        # Debug logging
        print(f"Admin view - User: {self.request.user}, is_staff: {self.request.user.is_staff}")

        # Admin can see all events
        if self.request.user.is_staff:
            queryset = Event.objects.all().select_related('category', 'created_by').prefetch_related('images')
            print(f"Admin queryset count: {queryset.count()}")
            return queryset
        # Regular users can only see their own events
        queryset = Event.objects.filter(
            created_by=self.request.user
        ).select_related('category', 'created_by').prefetch_related('images')
        print(f"User queryset count: {queryset.count()}")
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventCreateUpdateSerializer
        return EventPreviewSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class EventAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin view for managing individual events"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Event.objects.all().select_related('category', 'created_by').prefetch_related('images')
        return Event.objects.filter(
            created_by=self.request.user
        ).select_related('category', 'created_by').prefetch_related('images')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer

class EventPublishView(generics.UpdateAPIView):
    """Publish an event (admin only)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Event.objects.all()
        return Event.objects.filter(created_by=self.request.user)

    def patch(self, request, *args, **kwargs):
        event = self.get_object()

        if event.status == 'published':
            return Response(
                {'detail': 'Event is already published'},
                status=status.HTTP_400_BAD_REQUEST
            )

        event.status = 'published'
        event.published_at = timezone.now()
        event.save()

        return Response({
            'detail': 'Event published successfully',
            'published_at': event.published_at
        })

class EventArchiveView(generics.UpdateAPIView):
    """Archive an event (admin only)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Event.objects.all()
        return Event.objects.filter(created_by=self.request.user)

    def patch(self, request, *args, **kwargs):
        event = self.get_object()
        event.status = 'archived'
        event.save()

        return Response({'detail': 'Event archived successfully'})

# REGISTRATION VIEWS (Optional feature)
class EventRegistrationView(generics.CreateAPIView):
    """Register for an event"""
    serializer_class = EventRegistrationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        event_slug = kwargs.get('slug')
        event = get_object_or_404(Event, slug=event_slug, status='published', is_active=True)

        # Check if registration is required
        if not event.registration_required:
            return Response(
                {'detail': 'Registration is not required for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if registration is open
        if not event.registration_open:
            return Response(
                {'detail': 'Registration is closed for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check capacity
        if event.max_attendees and event.attendee_count >= event.max_attendees:
            return Response(
                {'detail': 'Event is full'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already registered
        if EventRegistration.objects.filter(
            user=request.user,
            event=event,
            is_canceled=False
        ).exists():
            return Response(
                {'detail': 'Already registered for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create registration
        registration = EventRegistration.objects.create(
            user=request.user,
            event=event,
            registration_data=request.data.get('registration_data', {}),
            notes=request.data.get('notes', '')
        )

        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class EventUnregisterView(generics.UpdateAPIView):
    """Unregister from an event"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        event_slug = kwargs.get('slug')
        event = get_object_or_404(Event, slug=event_slug)

        try:
            registration = EventRegistration.objects.get(
                user=request.user,
                event=event,
                is_canceled=False
            )
            registration.is_canceled = True
            registration.save()

            return Response({'detail': 'Successfully unregistered from event'})
        except EventRegistration.DoesNotExist:
            return Response(
                {'detail': 'No active registration found'},
                status=status.HTTP_404_NOT_FOUND
            )
