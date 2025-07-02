from django.urls import path
from .views import DocumentationView ,DocumentationDetailView,DocumentationActivateView

urlpatterns = [
    path('', DocumentationView.as_view(), name='Documentation-list'),
    path('<int:pk>/', DocumentationDetailView.as_view(), name='Documentation-details'),
    path('<int:pk>/activate/', DocumentationActivateView.as_view(), name='Documentation-activate'),
]