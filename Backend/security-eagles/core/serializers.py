
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PointsTransaction, PointsReward

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
            'total_points',
            'available_points',
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
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'created_at', 'updated_at', 'total_points', 'available_points']

    def create(self, validated_data):
        # Handle created_by if needed
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        user = super().create(validated_data)
        return user


class PointsTransactionSerializer(serializers.ModelSerializer):
    """Serializer for points transactions"""

    user_username = serializers.CharField(source='user.username', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = PointsTransaction
        fields = [
            'id', 'user', 'user_username', 'transaction_type', 'transaction_type_display',
            'amount', 'source', 'source_display', 'description', 'related_object_id',
            'related_object_type', 'balance_after', 'created_at', 'created_by',
            'is_reversed', 'reversed_by', 'reversed_at'
        ]
        read_only_fields = [
            'id', 'user_username', 'transaction_type_display', 'source_display',
            'balance_after', 'created_at', 'created_by', 'is_reversed',
            'reversed_by', 'reversed_at'
        ]


class PointsRewardSerializer(serializers.ModelSerializer):
    """Serializer for points rewards configuration"""

    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)

    class Meta:
        model = PointsReward
        fields = [
            'id', 'activity_type', 'activity_type_display', 'points_amount',
            'is_active', 'description', 'max_per_day', 'max_per_week',
            'max_total', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'activity_type_display', 'created_at', 'updated_at']


class UserPointsSerializer(serializers.ModelSerializer):
    """Simplified serializer for user points information"""

    recent_transactions = serializers.SerializerMethodField()
    points_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'total_points', 'available_points',
            'recent_transactions', 'points_breakdown'
        ]
        read_only_fields = ['id', 'username', 'total_points', 'available_points']

    def get_recent_transactions(self, obj):
        """Get recent points transactions"""
        recent = obj.points_transactions.all()[:5]
        return PointsTransactionSerializer(recent, many=True).data

    def get_points_breakdown(self, obj):
        """Get points breakdown by source"""
        from django.db.models import Sum

        breakdown = obj.points_transactions.filter(
            transaction_type='earned'
        ).values('source').annotate(
            total_points=Sum('amount')
        ).order_by('-total_points')

        return list(breakdown)


class SpendPointsSerializer(serializers.Serializer):
    """Serializer for spending points"""

    amount = serializers.IntegerField(min_value=1)
    purpose = serializers.ChoiceField(choices=PointsTransaction.POINT_SOURCES)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    related_object_id = serializers.IntegerField(required=False, allow_null=True)
    related_object_type = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_amount(self, value):
        """Validate user has enough points"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.available_points < value:
                raise serializers.ValidationError(
                    f"Insufficient points. Available: {request.user.available_points}, Required: {value}"
                )
        return value

    def update(self, instance, validated_data):
        # Prevent changing 'created_by' after creation
        validated_data.pop('created_by', None)
        return super().update(instance, validated_data)
