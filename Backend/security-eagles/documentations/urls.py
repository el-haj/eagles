from django.urls import path
from .views import DocumentationView ,DocumentationDetailView,DocumentationActivateView, DocumentationAccordionView, DocumentationMarkdownContentView

urlpatterns = [
    path('', DocumentationView.as_view(), name='Documentation-list'),
    path('<int:pk>/', DocumentationDetailView.as_view(), name='Documentation-details'),
    path('<int:pk>/activate/', DocumentationActivateView.as_view(), name='Documentation-activate'),
    path('accordion/', DocumentationAccordionView.as_view(), name='documentation-accordion'),
    path('<int:pk>/markdown/', DocumentationMarkdownContentView.as_view(), name='documentation-markdown'),
]