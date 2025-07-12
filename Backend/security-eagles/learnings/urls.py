from django.urls import path
from .views import (
    # Track views (no auth required)
    TrackListView, TrackDetailView, TrackByCategoryView,
    
    # Learning path views (auth required)
    LearningPathListView, LearningPathDetailView, LearningPathEnrollView,
    LearningPathUnenrollView, MarkSectionCompleteView, UserLearningProgressListView,
    
    # Comment views
    LearningCommentListCreateView, LearningCommentDetailView, LearningCommentRepliesView,
    
    # Rating views
    LearningRatingListCreateView, LearningRatingDetailView
)

urlpatterns = [
    # Track endpoints (no authentication required)
    path('tracks/', TrackListView.as_view(), name='track-list'),
    path('tracks/<int:id>/', TrackDetailView.as_view(), name='track-detail'),
    path('tracks/category/<str:category>/', TrackByCategoryView.as_view(), name='track-by-category'),
    
    # Learning path endpoints (authentication required)
    path('learning-paths/', LearningPathListView.as_view(), name='learning-path-list'),
    path('learning-paths/<int:id>/', LearningPathDetailView.as_view(), name='learning-path-detail'),
    path('learning-paths/<int:learning_path_id>/enroll/', LearningPathEnrollView.as_view(), name='learning-path-enroll'),
    path('learning-paths/<int:learning_path_id>/unenroll/', LearningPathUnenrollView.as_view(), name='learning-path-unenroll'),
    
    # Section completion
    path('sections/<int:section_id>/complete/', MarkSectionCompleteView.as_view(), name='section-complete'),
    
    # User progress
    path('my-progress/', UserLearningProgressListView.as_view(), name='user-learning-progress'),
    
    # Comments
    path('learning-paths/<int:learning_path_id>/comments/', LearningCommentListCreateView.as_view(), name='learning-comments'),
    path('comments/<int:pk>/', LearningCommentDetailView.as_view(), name='learning-comment-detail'),
    path('comments/<int:comment_id>/replies/', LearningCommentRepliesView.as_view(), name='learning-comment-replies'),
    
    # Ratings
    path('learning-paths/<int:learning_path_id>/ratings/', LearningRatingListCreateView.as_view(), name='learning-ratings'),
    path('ratings/<int:pk>/', LearningRatingDetailView.as_view(), name='learning-rating-detail'),
]
