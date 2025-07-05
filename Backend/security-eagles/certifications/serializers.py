from rest_framework import serializers
from .models import Certification, UserCertification

class CertificationListSerializer(serializers.ModelSerializer):
    badge_pic_url = serializers.SerializerMethodField()

    class Meta:
        model = Certification
        fields = [
            'id', 'name', 'category', 'difficulty', 'is_pro', 'price',
            'is_active', 'badge_pic_url'
        ]

    def get_badge_pic_url(self, obj):
        request = self.context.get('request')
        if obj.badge_pic and hasattr(obj.badge_pic, 'url'):
            if request:
                return request.build_absolute_uri(obj.badge_pic.url)
            return obj.badge_pic.url
        return None

class CertificationDetailSerializer(serializers.ModelSerializer):
    badge_pic_url = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Certification
        fields = [
            'id', 'name', 'description', 'category', 'difficulty', 'is_pro', 'price',
            'badge_pic', 'badge_pic_url', 'test_url', 'required_completion',
            'is_active', 'recurring_time', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_badge_pic_url(self, obj):
        request = self.context.get('request')
        if obj.badge_pic and hasattr(obj.badge_pic, 'url'):
            if request:
                return request.build_absolute_uri(obj.badge_pic.url)
            return obj.badge_pic.url
        return None

class UserCertificationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    certification = serializers.StringRelatedField()

    class Meta:
        model = UserCertification
        fields = [
            'id', 'user', 'certification', 'done_at', 'completion', 'last_attend'
            ]