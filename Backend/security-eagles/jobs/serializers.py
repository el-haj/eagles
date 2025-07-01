from rest_framework import serializers
from .models import Job, JobPost

class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    is_applied = serializers.SerializerMethodField()
    application_count = serializers.IntegerField(read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = '__all__'

    def get_is_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobPost.objects.filter(job=obj, user=request.user).exists()
        return False

    def get_logo_url(self, obj):
        if obj.logo and hasattr(obj.logo, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
