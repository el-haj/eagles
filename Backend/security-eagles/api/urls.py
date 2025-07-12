from django.urls import path, include
from .views import HelloWorldView
from .dashboard_views import DashboardSummaryView, DashboardActivityView, DashboardFeaturedView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path('hello/', HelloWorldView.as_view(), name='hello'),
    path('news/', include('news.urls')),
    path('events/', include('events.urls')),
    path('jobs/', include('jobs.urls')),
    path('learnings/', include('learnings.urls')),
    path('labs/', include('labs.urls')),
    path('users/', include('users.urls')),
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/activity/', DashboardActivityView.as_view(), name='dashboard-activity'),
    path('dashboard/featured/', DashboardFeaturedView.as_view(), name='dashboard-featured'),
    # path('auth/', include('rest_framework_social_oauth2.urls')),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
] 



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)