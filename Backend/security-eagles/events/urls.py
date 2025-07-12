from django.urls import path
from .views import (
    # Public views
    EventListView, EventDetailView, EventCategoryListView,
    FeaturedEventsView, UpcomingEventsView, OngoingEventsView,
    PastEventsView, EventSearchView,

    # Admin views
    EventAdminListView, EventAdminDetailView, EventPublishView, EventArchiveView,

    # Registration views
    EventRegistrationView, EventUnregisterView
)

urlpatterns = [
    # Public endpoints
    path('', EventListView.as_view(), name='event-list'),
    path('categories/', EventCategoryListView.as_view(), name='event-categories'),
    path('featured/', FeaturedEventsView.as_view(), name='featured-events'),
    path('upcoming/', UpcomingEventsView.as_view(), name='upcoming-events'),
    path('ongoing/', OngoingEventsView.as_view(), name='ongoing-events'),
    path('past/', PastEventsView.as_view(), name='past-events'),
    path('search/', EventSearchView.as_view(), name='event-search'),

    # Admin endpoints (must come before slug patterns)
    path('admin/', EventAdminListView.as_view(), name='event-admin-list'),
    path('admin/<slug:slug>/', EventAdminDetailView.as_view(), name='event-admin-detail'),
    path('admin/<slug:slug>/publish/', EventPublishView.as_view(), name='event-publish'),
    path('admin/<slug:slug>/archive/', EventArchiveView.as_view(), name='event-archive'),

    # Event detail and registration endpoints (must come after admin patterns)
    path('<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('<slug:slug>/register/', EventRegistrationView.as_view(), name='event-register'),
    path('<slug:slug>/unregister/', EventUnregisterView.as_view(), name='event-unregister'),
]