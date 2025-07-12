
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from .serializers import (
    UserSerializer, PointsTransactionSerializer, PointsRewardSerializer,
    UserPointsSerializer, SpendPointsSerializer
)
from .models import PointsTransaction, PointsReward
from .permissions import ISAdminOrReadOwn

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer

    permission_classes = [permissions.IsAuthenticated,
                          ISAdminOrReadOwn]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        if self.action in ['create']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """Get current user's profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def points(self, request):
        """Get current user's points information"""
        serializer = UserPointsSerializer(request.user)
        return Response(serializer.data)


class PointsTransactionListView(generics.ListAPIView):
    """List user's points transactions"""
    serializer_class = PointsTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PointsTransaction.objects.filter(user=self.request.user)

        # Filter by transaction type
        transaction_type = self.request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        # Filter by source
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source=source)

        # Filter by date range
        days = self.request.query_params.get('days')
        if days:
            try:
                days_int = int(days)
                since = timezone.now() - timedelta(days=days_int)
                queryset = queryset.filter(created_at__gte=since)
            except ValueError:
                pass

        return queryset.order_by('-created_at')


class SpendPointsView(APIView):
    """Spend user points"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SpendPointsSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Spend the points
            success = request.user.spend_points(
                amount=serializer.validated_data['amount'],
                purpose=serializer.validated_data['purpose'],
                description=serializer.validated_data.get('description', ''),
                related_object_id=serializer.validated_data.get('related_object_id'),
                related_object_type=serializer.validated_data.get('related_object_type')
            )

            if success:
                return Response({
                    'success': True,
                    'message': 'Points spent successfully',
                    'remaining_points': request.user.available_points
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to spend points'
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PointsLeaderboardView(APIView):
    """Get points leaderboard"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        # Get top users by total points
        top_users = User.objects.filter(
            is_active=True
        ).order_by('-total_points')[:20]

        leaderboard = []
        for i, user in enumerate(top_users, 1):
            leaderboard.append({
                'rank': i,
                'username': user.username,
                'total_points': user.total_points,
                'available_points': user.available_points
            })

        return Response({'leaderboard': leaderboard})


class PointsStatsView(APIView):
    """Get points system statistics"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # User's points breakdown
        earned_breakdown = user.points_transactions.filter(
            transaction_type='earned'
        ).values('source').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        spent_breakdown = user.points_transactions.filter(
            transaction_type='spent'
        ).values('source').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_earned = user.points_transactions.filter(
            transaction_type='earned',
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0

        recent_spent = user.points_transactions.filter(
            transaction_type='spent',
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0

        stats = {
            'current_points': {
                'total': user.total_points,
                'available': user.available_points,
                'spent': user.total_points - user.available_points
            },
            'recent_activity': {
                'earned_last_30_days': recent_earned,
                'spent_last_30_days': recent_spent
            },
            'breakdown': {
                'earned_by_source': list(earned_breakdown),
                'spent_by_purpose': list(spent_breakdown)
            }
        }

        return Response(stats)


# Admin views for points management
class PointsRewardViewSet(viewsets.ModelViewSet):
    """Admin management of points rewards"""
    queryset = PointsReward.objects.all()
    serializer_class = PointsRewardSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminPointsTransactionView(generics.ListAPIView):
    """Admin view of all points transactions"""
    queryset = PointsTransaction.objects.all().order_by('-created_at')
    serializer_class = PointsTransactionSerializer
    permission_classes = [permissions.IsAdminUser]
