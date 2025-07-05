from django.urls import path, include
from .views import HelloWorldView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('hello/', HelloWorldView.as_view(), name='hello'),
    path('news/', include('news.urls')),
    path('events/', include('events.urls')),
    path('jobs/', include('jobs.urls')),
    path('learning/', include('learning.urls')),
    path('labs/', include('labs.urls')),
    
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)