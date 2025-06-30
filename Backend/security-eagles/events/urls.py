from django.urls import path
from .views import EventListCreateView, EventRegisterView

urlpatterns = [
    path('', EventListCreateView.as_view(), name='event-list-create'),
    path('<int:event_id>/register/', EventRegisterView.as_view(), name='event-register'),
]