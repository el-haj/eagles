from django.urls import path
from .views import (
    # New comprehensive views
    JobCategoryListView, JobListView, JobDetailView,
    JobApplicationCreateView, JobApplicationListView, JobApplicationDetailView,
    JobApplicationWithdrawView, JobAdminListView, JobAdminDetailView,
    JobApplicationAdminListView, JobApplicationAdminDetailView,
    # Legacy views for backward compatibility
    JobListCreateView, JobApplyView, JobUnapplyView
)

urlpatterns = [
    # Job Categories
    path('categories/', JobCategoryListView.as_view(), name='job-categories'),

    # Public Job Views
    path('', JobListView.as_view(), name='job-list'),
    path('<int:id>/', JobDetailView.as_view(), name='job-detail'),

    # Job Applications
    path('applications/', JobApplicationListView.as_view(), name='job-applications'),
    path('applications/create/', JobApplicationCreateView.as_view(), name='job-application-create'),
    path('applications/<int:pk>/', JobApplicationDetailView.as_view(), name='job-application-detail'),
    path('applications/<int:pk>/withdraw/', JobApplicationWithdrawView.as_view(), name='job-application-withdraw'),

    # Admin Job Management
    path('admin/jobs/', JobAdminListView.as_view(), name='job-admin-list'),
    path('admin/jobs/<int:pk>/', JobAdminDetailView.as_view(), name='job-admin-detail'),
    path('admin/applications/', JobApplicationAdminListView.as_view(), name='job-application-admin-list'),
    path('admin/applications/<int:pk>/', JobApplicationAdminDetailView.as_view(), name='job-application-admin-detail'),

    # Legacy endpoints for backward compatibility
    path('legacy/', JobListCreateView.as_view(), name='job-list-create-legacy'),
    path('legacy/<int:job_id>/apply/', JobApplyView.as_view(), name='job-apply-legacy'),
    path('legacy/<int:job_id>/unapply/', JobUnapplyView.as_view(), name='job-unapply-legacy'),
]
