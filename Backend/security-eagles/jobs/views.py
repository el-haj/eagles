from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q, F
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from rest_framework.pagination import PageNumberPagination

from .models import JobCategory, Job, JobApplication, JobView, JobPost
from .serializers import (
    JobCategorySerializer, JobListSerializer, JobDetailSerializer,
    JobApplicationSerializer, JobApplicationCreateSerializer, 
    JobApplicationAdminSerializer, JobSerializer, JobPostSerializer
)

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class JobFilter(django_filters.FilterSet):
    """Filter class for job listings"""
    search = django_filters.CharFilter(method='filter_search')
    category = django_filters.ModelChoiceFilter(queryset=JobCategory.objects.all())
    job_type = django_filters.ChoiceFilter(choices=Job.JOB_TYPE_CHOICES)
    employment_type = django_filters.ChoiceFilter(choices=Job.EMPLOYMENT_TYPE_CHOICES)
    experience_level = django_filters.ChoiceFilter(choices=Job.EXPERIENCE_LEVEL_CHOICES)
    is_remote = django_filters.BooleanFilter()
    remote_type = django_filters.ChoiceFilter(choices=[
        ('fully_remote', 'Fully Remote'),
        ('hybrid', 'Hybrid'),
        ('on_site', 'On-Site'),
    ])
    location = django_filters.CharFilter(lookup_expr='icontains')
    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    tags = django_filters.CharFilter(method='filter_tags')
    is_featured = django_filters.BooleanFilter()
    is_urgent = django_filters.BooleanFilter()
    
    class Meta:
        model = Job
        fields = []
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(company_name__icontains=value) |
            Q(requirements__icontains=value) |
            Q(responsibilities__icontains=value)
        )
    
    def filter_tags(self, queryset, name, value):
        tags = [tag.strip() for tag in value.split(',')]
        return queryset.filter(tags__overlap=tags)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

# Job Category Views
class JobCategoryListView(generics.ListAPIView):
    """List all job categories"""
    queryset = JobCategory.objects.filter(is_active=True).order_by('name')
    serializer_class = JobCategorySerializer
    permission_classes = [IsAuthenticated]

# Job Views
class JobListView(generics.ListAPIView):
    """List jobs with filtering and search"""
    serializer_class = JobListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilter
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Job.objects.filter(
            status='published'
        ).select_related('category', 'posted_by').order_by(
            '-is_featured', '-is_urgent', '-created_at'
        )

class JobDetailView(generics.RetrieveAPIView):
    """Get detailed job information"""
    queryset = Job.objects.filter(status='published')
    serializer_class = JobDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track job view
        JobView.objects.create(
            job=instance,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Increment view count
        Job.objects.filter(id=instance.id).update(view_count=F('view_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# Job Application Views
class JobApplicationCreateView(generics.CreateAPIView):
    """Apply for a job"""
    serializer_class = JobApplicationCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        application = serializer.save(user=self.request.user)
        # Increment application count
        Job.objects.filter(id=application.job.id).update(application_count=F('application_count') + 1)

class JobApplicationListView(generics.ListAPIView):
    """List user's job applications"""
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return JobApplication.objects.filter(
            user=self.request.user
        ).select_related('job', 'job__category').order_by('-created_at')

class JobApplicationDetailView(generics.RetrieveUpdateAPIView):
    """Get/update specific job application"""
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)

class JobApplicationWithdrawView(APIView):
    """Withdraw a job application"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            application = JobApplication.objects.get(pk=pk, user=request.user)
            if application.status in ['accepted', 'rejected']:
                return Response(
                    {"detail": "Cannot withdraw application that has been processed."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            application.status = 'withdrawn'
            application.save()
            
            # Decrement application count
            Job.objects.filter(id=application.job.id).update(
                application_count=F('application_count') - 1
            )
            
            return Response({"detail": "Application withdrawn successfully."})
            
        except JobApplication.DoesNotExist:
            return Response(
                {"detail": "Application not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

# Admin Views for Job Management
class JobAdminListView(generics.ListCreateAPIView):
    """Admin view for managing all jobs"""
    serializer_class = JobDetailSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilter
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Job.objects.all().select_related('category', 'posted_by').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

class JobAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin view for managing specific job"""
    queryset = Job.objects.all()
    serializer_class = JobDetailSerializer
    permission_classes = [IsAdminUser]

class JobApplicationAdminListView(generics.ListAPIView):
    """Admin view for managing job applications"""
    serializer_class = JobApplicationAdminSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardResultsSetPagination
    
    filterset_fields = ['status', 'job', 'job__category', 'job__job_type']
    
    def get_queryset(self):
        return JobApplication.objects.all().select_related(
            'user', 'job', 'job__category'
        ).order_by('-created_at')

class JobApplicationAdminDetailView(generics.RetrieveUpdateAPIView):
    """Admin view for managing specific job application"""
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationAdminSerializer
    permission_classes = [IsAdminUser]

# Legacy Views (for backward compatibility)
class JobListCreateView(APIView):
    """Legacy view - use JobListView and JobAdminListView instead"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filter/search parameters
        search = request.query_params.get('search')
        category = request.query_params.get('category')
        location = request.query_params.get('location')
        job_type = request.query_params.get('job_type')
        experience_level = request.query_params.get('experience_level')
        is_remote = request.query_params.get('is_remote')

        jobs = Job.objects.filter(status='published').order_by('-created_at')

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(requirements__icontains=search) |
                Q(responsibilities__icontains=search) |
                Q(company_name__icontains=search)
            )
        if category:
            jobs = jobs.filter(category__name__iexact=category)
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
    """Legacy apply view - use JobApplicationCreateView instead"""
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        user = request.user
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        if JobApplication.objects.filter(user=user, job=job).exists():
            return Response({"detail": "Already applied to this job."}, status=status.HTTP_400_BAD_REQUEST)

        # Create new application
        application_data = {
            'job': job.id,
            'cover_letter': request.data.get('message', 'I am interested in this position.'),
            'portfolio_links': request.data.get('portfolio_links', [])
        }
        
        serializer = JobApplicationCreateSerializer(data=application_data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"detail": "Application submitted."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobUnapplyView(APIView):
    """Legacy unapply view - use JobApplicationWithdrawView instead"""
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        user = request.user
        try:
            application = JobApplication.objects.get(user=user, job_id=job_id)
            application.status = 'withdrawn'
            application.save()
            
            # Decrement application count
            Job.objects.filter(id=job_id).update(
                application_count=F('application_count') - 1
            )
            
            return Response({"detail": "Application removed."}, status=status.HTTP_200_OK)
            
        except JobApplication.DoesNotExist:
            return Response({"detail": "You have not applied to this job."}, status=status.HTTP_404_NOT_FOUND)
