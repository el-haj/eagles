from rest_framework import serializers
from .models import JobCategory, Job, JobApplication, JobView, JobPost
from django.contrib.auth import get_user_model

User = get_user_model()

class JobCategorySerializer(serializers.ModelSerializer):
    job_count = serializers.SerializerMethodField()

    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'description', 'job_count', 'is_active']

    def get_job_count(self, obj):
        return obj.jobs.filter(status='published').count()

class JobListSerializer(serializers.ModelSerializer):
    """Serializer for job list view with essential fields"""
    is_applied = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    company_logo_url = serializers.SerializerMethodField()
    salary_range_display = serializers.ReadOnlyField()
    days_until_deadline = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'company_logo_url', 'location',
            'job_type', 'employment_type', 'experience_level', 'category_name',
            'is_remote', 'remote_type', 'salary_range_display', 'tags',
            'application_deadline', 'days_until_deadline', 'is_featured', 'is_urgent',
            'application_count', 'view_count', 'is_applied', 'is_active', 'created_at'
        ]

    def get_is_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobApplication.objects.filter(job=obj, user=request.user).exists()
        return False

    def get_company_logo_url(self, obj):
        if obj.company_logo and hasattr(obj.company_logo, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.company_logo.url)
            return obj.company_logo.url
        return None

class JobDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed job view"""
    is_applied = serializers.SerializerMethodField()
    user_application = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    company_logo_url = serializers.SerializerMethodField()
    salary_range_display = serializers.ReadOnlyField()
    days_until_deadline = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    posted_by_name = serializers.CharField(source='posted_by.username', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
        extra_fields = [
            'is_applied', 'user_application', 'category_name', 'company_logo_url',
            'salary_range_display', 'days_until_deadline', 'is_active', 'posted_by_name'
        ]

    def get_is_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobApplication.objects.filter(job=obj, user=request.user).exists()
        return False

    def get_user_application(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                application = JobApplication.objects.get(job=obj, user=request.user)
                return {
                    'id': application.id,
                    'status': application.status,
                    'created_at': application.created_at,
                    'updated_at': application.updated_at,
                }
            except JobApplication.DoesNotExist:
                pass
        return None

    def get_company_logo_url(self, obj):
        if obj.company_logo and hasattr(obj.company_logo, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.company_logo.url)
            return obj.company_logo.url
        return None

class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job applications"""
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    applicant_name = serializers.ReadOnlyField()
    days_since_applied = serializers.ReadOnlyField()

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'company_name', 'cover_letter',
            'resume_file', 'portfolio_links', 'status', 'applicant_name',
            'days_since_applied', 'created_at', 'updated_at'
        ]
        read_only_fields = ['applicant_profile', 'admin_notes', 'rating']

class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating job applications"""

    class Meta:
        model = JobApplication
        fields = ['job', 'cover_letter', 'resume_file', 'portfolio_links']

    def validate_job(self, value):
        """Validate that user hasn't already applied to this job"""
        user = self.context['request'].user
        if JobApplication.objects.filter(user=user, job=value).exists():
            raise serializers.ValidationError("You have already applied to this job.")

        if not value.is_active:
            raise serializers.ValidationError("This job is no longer accepting applications.")

        return value

class JobApplicationAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin management of applications"""
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    applicant_name = serializers.ReadOnlyField()
    applicant_email = serializers.CharField(source='user.email', read_only=True)
    days_since_applied = serializers.ReadOnlyField()

    class Meta:
        model = JobApplication
        fields = '__all__'

# Legacy serializers for backward compatibility
class JobSerializer(serializers.ModelSerializer):
    """Legacy serializer - use JobListSerializer or JobDetailSerializer instead"""
    is_applied = serializers.SerializerMethodField()
    application_count = serializers.IntegerField(read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = '__all__'

    def get_is_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobApplication.objects.filter(job=obj, user=request.user).exists()
        return False

    def get_logo_url(self, obj):
        if obj.company_logo and hasattr(obj.company_logo, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.company_logo.url)
            return obj.company_logo.url
        return None

class JobPostSerializer(serializers.ModelSerializer):
    """Legacy serializer - use JobApplicationSerializer instead"""
    class Meta:
        model = JobPost
        fields = '__all__'
