from django.urls import path, include
from . import views



# Public URLs (no authentication required for reading)
public_patterns = [
    # News listing and filtering
    path('', views.NewsPreviewListView.as_view(), name='list'),
    path('featured/', views.FeaturedNewsListView.as_view(), name='featured'),
    path('breaking/', views.BreakingNewsListView.as_view(), name='breaking'),
    path('latest/', views.LatestNewsListView.as_view(), name='latest'),
    path('search/', views.news_search, name='search'),

    # Categories
    path('categories/', views.NewsCategoryListView.as_view(), name='categories'),

    # Individual article
    path('<slug:slug>/', views.NewsDetailView.as_view(), name='detail'),

    # Comments (read/write with auth)
    path('<slug:slug>/comments/', views.NewsCommentListCreateView.as_view(), name='comments'),

    # User interactions (require authentication)
    path('<slug:slug>/like/', views.NewsLikeToggleView.as_view(), name='like_toggle'),
]

# Admin URLs (require staff/admin permissions)
admin_patterns = [
    # News management
    path('', views.NewsAdminListCreateView.as_view(), name='admin_list'),
    path('<slug:slug>/', views.NewsAdminDetailView.as_view(), name='admin_detail'),
    path('<slug:slug>/publish/', views.NewsPublishToggleView.as_view(), name='admin_publish'),
    path('<slug:slug>/images/', views.NewsImageUploadView.as_view(), name='admin_image_upload'),

    # Analytics
    path('analytics/', views.NewsAnalyticsView.as_view(), name='admin_analytics'),
]

urlpatterns = [
    # Public news endpoints
    path('', include(public_patterns)),

    # Admin news endpoints
    path('admin/', include(admin_patterns)),
]
