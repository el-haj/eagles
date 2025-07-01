from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q

from .models import Job, JobPost
from .serializers import JobSerializer, JobPostSerializer

class JobListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        # Filter/search parameters
        search = request.query_params.get('search')
        category = request.query_params.get('category')
        location = request.query_params.get('location')
        job_type = request.query_params.get('job_type')
        experience_level = request.query_params.get('experience_level')
        is_remote = request.query_params.get('is_remote')

        jobs = Job.objects.all().order_by('-created_at')

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(requirements__icontains=search) |
                Q(responsibilities__icontains=search) |
                Q(company_name__icontains=search)
            )
        if category:
            jobs = jobs.filter(category__iexact=category)
        if location:
            jobs = jobs.filter(location__icontains=location)
        if job_type:
            jobs = jobs.filter(job_type__iexact=job_type)
        if experience_level:
            jobs = jobs.filter(experience_level__iexact=experience_level)
        if is_remote is not None:
            if is_remote.lower() == 'true':
                jobs = jobs.filter(is_remote=True)
            elif is_remote.lower() == 'false':
                jobs = jobs.filter(is_remote=False)

        serializer = JobSerializer(jobs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can create jobs."}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobApplyView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, job_id):
        user = request.user
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        if JobPost.objects.filter(user=user, job=job).exists():
            return Response({"detail": "Already applied to this job."}, status=status.HTTP_400_BAD_REQUEST)

        JobPost.objects.create(user=user, job=job, meta_data=request.data.get('meta_data', {}))
        job.application_count += 1
        job.save()

        return Response({"detail": "Application submitted."}, status=status.HTTP_201_CREATED)

class JobUnapplyView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, job_id):
        user = request.user
        try:
            job_post = JobPost.objects.get(user=user, job_id=job_id)
        except JobPost.DoesNotExist:
            return Response({"detail": "You have not applied to this job."}, status=status.HTTP_404_NOT_FOUND)

        job_post.delete()
        job = Job.objects.get(id=job_id)
        job.application_count = max(job.application_count - 1, 0)
        job.save()

        return Response({"detail": "Application removed."}, status=status.HTTP_200_OK)
