from django.urls import path, include
from .views import HelloWorldView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('hello/', HelloWorldView.as_view(), name='hello'),
    path('news/', include('news.urls')),
    #path('users/', include('core.urls')),  # Include user-related URLs
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)