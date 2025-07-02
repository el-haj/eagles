from django.urls import path
from .views import (
    LearningPathListCreateView,
    UserLearningListCreateView,
    UserLearningUpdateView
)

urlpatterns = [
    path('learning-paths/', LearningPathListCreateView.as_view(), name='learning-path-list'),
    path('user-learnings/', UserLearningListCreateView.as_view(), name='user-learning-list'),
    path('user-learnings/<int:id>/', UserLearningUpdateView.as_view(), name='user-learning-update'),
]
