from django.urls import path
from . import views

urlpatterns = [
    # Lab endpoints
    path('', views.LabListView.as_view(), name='lab-list'),
    path('latest/', views.LatestLabsView.as_view(), name='latest-labs'),
    path('featured/', views.FeaturedLabsView.as_view(), name='featured-labs'),
    path('<int:pk>/', views.LabDetailView.as_view(), name='lab-detail'),
    path('<int:lab_id>/access-check/', views.LabAccessCheckView.as_view(), name='lab-access-check'),
    path('<int:lab_id>/start/', views.StartLabView.as_view(), name='lab-start'),
    path('<int:lab_id>/leaderboard/', views.LabLeaderboardView.as_view(), name='lab-leaderboard'),

    # User lab attempts
    path('attempts/', views.UserLabListView.as_view(), name='user-lab-list'),
    path('attempts/<int:pk>/', views.UserLabDetailView.as_view(), name='user-lab-detail'),
    path('attempts/stats/', views.UserLabStatsView.as_view(), name='user-lab-stats'),

    # Lab redirection and return
    path('return/<str:token>/', views.LabReturnView.as_view(), name='lab-return'),

    # External system integration
    path('external/submit/', views.ExternalLabResultView.as_view(), name='external-lab-submit'),

    # Leaderboards
    path('leaderboard/', views.LabLeaderboardView.as_view(), name='overall-leaderboard'),
]
