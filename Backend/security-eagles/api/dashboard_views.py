from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from news.models import News
from events.models import Event
from jobs.models import Job
from labs.models import Lab
from learnings.models import LearningPath, UserLearningProgress

User = get_user_model()

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        total_learning_paths = LearningPath.objects.count()
        completed_learning_paths = UserLearningProgress.objects.filter(user=user, status='completed').count()
        in_progress_learning_paths = UserLearningProgress.objects.filter(user=user, status='in_progress').count()
        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
            "stats": {
                "learning_paths_total": total_learning_paths,
                "learning_paths_completed": completed_learning_paths,
                "learning_paths_in_progress": in_progress_learning_paths,
                "events": Event.objects.count(),
                "jobs": Job.objects.count(),
                "labs": Lab.objects.count(),
            }
        })

class DashboardActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Dummy data, replace with real user activity
        return Response([
            {"type": "job_applied", "detail": "Applied to Security Analyst at CyberCorp", "timestamp": "2025-07-04T10:00:00Z"},
            {"type": "course_completed", "detail": "Completed 'Intro to Threat Hunting'", "timestamp": "2025-07-03T15:00:00Z"},
            {"type": "event_registered", "detail": "Registered for Blue Team Summit", "timestamp": "2025-07-02T12:00:00Z"},
        ])

class DashboardFeaturedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        featured_news = News.objects.order_by('-published_at')[:3]
        featured_events = Event.objects.order_by('-start_time')[:3]
        featured_jobs = Job.objects.order_by('-created_at')[:3]
        return Response({
            "news": [{"id": n.id, "title": n.title, "image": getattr(n, "image", None)} for n in featured_news],
            "events": [{"id": e.id, "title": e.title, "image": getattr(e, "image", None)} for e in featured_events],
            "jobs": [{"id": j.id, "title": j.title, "company": j.company_name, "image": getattr(j, "image", None)} for j in featured_jobs],
        })
