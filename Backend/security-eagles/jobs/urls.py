from django.urls import path
from .views import JobListCreateView, JobApplyView, JobUnapplyView

urlpatterns = [
    path('', JobListCreateView.as_view(), name='job-list-create'),
    path('<int:job_id>/apply/', JobApplyView.as_view(), name='job-apply'),
    path('<int:job_id>/unapply/', JobUnapplyView.as_view(), name='job-unapply'),
]
