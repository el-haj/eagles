from rest_framework import serializers
from .models import ContactMessage, ContactSettings


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contact messages (public API)"""
    
    class Meta:
        model = ContactMessage
        fields = [
            'name', 'email', 'phone', 'company',
            'subject', 'message'
        ]
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True},
            'message': {'required': True},
        }
    
    def validate_message(self, value):
        """Ensure message is not too short"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value.strip()
    
    def validate_name(self, value):
        """Clean and validate name"""
        return value.strip()


class ContactMessageListSerializer(serializers.ModelSerializer):
    """Serializer for listing contact messages (admin use)"""
    
    subject_display = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'company',
            'subject', 'subject_display', 'message',
            'status', 'status_display', 'is_read',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContactMessageDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed contact message view (admin use)"""
    
    subject_display = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'company',
            'subject', 'subject_display', 'message',
            'status', 'status_display', 'is_read',
            'ip_address', 'user_agent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'ip_address', 'user_agent']


class ContactSettingsSerializer(serializers.ModelSerializer):
    """Serializer for contact settings (public API)"""

    class Meta:
        model = ContactSettings
        fields = [
            'community_description', 'contact_email', 'discord_server',
            'availability_info', 'website_url', 'github_url',
            'twitter_url', 'linkedin_url', 'youtube_url'
        ]


class ContactSettingsAdminSerializer(serializers.ModelSerializer):
    """Serializer for contact settings (admin use)"""
    
    class Meta:
        model = ContactSettings
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContactSubjectChoicesSerializer(serializers.Serializer):
    """Serializer for returning subject choices"""
    
    value = serializers.CharField()
    label = serializers.CharField()
