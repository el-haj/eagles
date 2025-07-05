from django.urls import path
from .views import CertificationListView, CertificationDetailView, CertificationActivateView

urlpatterns = [
    path('', CertificationListView.as_view(), name='certification-list'),
    path('<int:pk>/', CertificationDetailView.as_view(), name='certification-detail'),
    path('<int:pk>/activate/', CertificationActivateView.as_view(), name='certification-activate'),
]