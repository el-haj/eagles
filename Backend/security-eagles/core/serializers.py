
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #todo : add only the needed fields !!
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'sso_provider',
            'sso_id',
            'score',
            'cv_url',
            'profile_pic',
            'github',
            'linkedin',
            'portfolio_url',
            'phone',
            'city',
            'type',
            'is_active',
            'is_staff',
            'is_superuser',
            'created_by',
            'created_at',
            'updated_at',
            'meta_data',
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Handle created_by if needed
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        user = super().create(validated_data)
        return user

    def update(self, instance, validated_data):
        # Prevent changing 'created_by' after creation
        validated_data.pop('created_by', None)
        return super().update(instance, validated_data)
