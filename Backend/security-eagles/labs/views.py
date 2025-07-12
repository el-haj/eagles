from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.db import models
from datetime import timedelta
import secrets
import logging

from .models import Lab, UserLab, LabRedirectSession
from .serializers import LabSerializer, UserLabSerializer
from core.models import PointsTransaction

logger = logging.getLogger(__name__)
class LabListView(generics.ListAPIView):
    """List all active labs with filtering and search"""
    serializer_class = LabSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Lab.objects.filter(status='active').order_by('-created_at')

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)

        # Search by name or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search)
            )

        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)

        return queryset


class LabDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific lab"""
    queryset = Lab.objects.filter(status='active')
    serializer_class = LabSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LatestLabsView(generics.ListAPIView):
    """Get latest 2 labs for homepage"""
    serializer_class = LabSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Lab.objects.filter(status='active').order_by('-created_at')[:2]


class FeaturedLabsView(generics.ListAPIView):
    """Get featured labs"""
    serializer_class = LabSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Lab.objects.filter(status='active', is_featured=True).order_by('-created_at')


class LabAccessCheckView(APIView):
    """Check if user can access a specific lab"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lab_id):
        lab = get_object_or_404(Lab, id=lab_id, status='active')

        can_attempt, message = lab.can_user_attempt(request.user)

        data = {
            'can_attempt': can_attempt,
            'message': message,
            'cooldown_remaining': lab.get_user_cooldown_remaining(request.user),
            'attempts_today': lab.get_user_attempts_today(request.user),
            'max_attempts_per_day': lab.max_attempts_per_day,
        }

        if not can_attempt:
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        return Response(data)


class StartLabView(APIView):
    """Start a lab attempt and create secure redirection"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lab_id):
        lab = get_object_or_404(Lab, id=lab_id, status='active')

        # Check if user can attempt this lab
        can_attempt, message = lab.can_user_attempt(request.user)
        if not can_attempt:
            return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)

        # Create user lab attempt
        user_lab = UserLab.objects.create(
            user=request.user,
            lab=lab,
            started_at=timezone.now(),
            status='started',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Generate secure redirect token
        redirect_token = user_lab.generate_redirect_token()

        # Create redirect session
        session_token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=4)  # 4 hour session

        # Build redirect URL with authentication
        base_url = lab.lab_url.rstrip('/')
        redirect_url = f"{base_url}?token={redirect_token}&session={session_token}&user_id={request.user.id}&lab_id={lab.id}"

        # Build return URL
        return_url = request.build_absolute_uri(reverse('lab-return', kwargs={'token': redirect_token}))

        redirect_session = LabRedirectSession.objects.create(
            user_lab=user_lab,
            session_token=session_token,
            redirect_url=redirect_url,
            return_url=return_url,
            expires_at=expires_at,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        logger.info(f"Lab attempt started: User {request.user.id}, Lab {lab.id}, Token {redirect_token}")

        return Response({
            'redirect_url': redirect_url,
            'return_url': return_url,
            'session_token': session_token,
            'expires_at': expires_at,
            'attempt_id': user_lab.id,
            'estimated_time': lab.estimated_time
        })

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LabReturnView(APIView):
    """Handle return from external lab system"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, token):
        """Handle GET return from external lab"""
        try:
            user_lab = UserLab.objects.get(redirect_token=token, user=request.user)

            # Check if session is still valid
            if user_lab.redirect_session.is_valid():
                return Response({
                    'message': 'Lab session is still active',
                    'status': 'active',
                    'attempt_id': user_lab.id,
                    'lab_name': user_lab.lab.name
                })
            else:
                return Response({
                    'message': 'Lab session has expired',
                    'status': 'expired',
                    'attempt_id': user_lab.id
                }, status=status.HTTP_410_GONE)

        except UserLab.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, token):
        """Handle POST return with results from external lab"""
        try:
            user_lab = UserLab.objects.get(redirect_token=token, user=request.user)

            # Validate session
            if not user_lab.redirect_session.is_valid():
                return Response({'error': 'Session expired'}, status=status.HTTP_410_GONE)

            # Mark session as used
            user_lab.redirect_session.mark_used()

            # Update user lab with results
            data = request.data
            user_lab.ended_at = timezone.now()
            user_lab.score = data.get('score')
            user_lab.time_spent = data.get('time_spent', user_lab.duration_minutes)
            user_lab.status = 'completed'
            user_lab.external_attempt_id = data.get('external_attempt_id')
            user_lab.notes = data.get('notes', '')

            user_lab.save()  # This will trigger point awarding

            logger.info(f"Lab completed: User {request.user.id}, Lab {user_lab.lab.id}, Score {user_lab.score}")

            return Response({
                'message': 'Lab results submitted successfully',
                'attempt_id': user_lab.id,
                'score': user_lab.score,
                'passed': user_lab.is_passed,
                'points_earned': user_lab.total_points_earned,
                'perfect_score': user_lab.is_perfect_score
            })

        except UserLab.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error processing lab return: {str(e)}")
            return Response({'error': 'Failed to process results'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLabListView(generics.ListAPIView):
    """List user's lab attempts"""
    serializer_class = UserLabSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = UserLab.objects.filter(user=self.request.user).order_by('-created_at')

        # Filter by lab
        lab_id = self.request.query_params.get('lab_id')
        if lab_id:
            queryset = queryset.filter(lab_id=lab_id)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by passed
        passed = self.request.query_params.get('passed')
        if passed is not None:
            queryset = queryset.filter(is_passed=passed.lower() == 'true')

        return queryset


class UserLabDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific lab attempt"""
    serializer_class = UserLabSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserLab.objects.filter(user=self.request.user)


class UserLabStatsView(APIView):
    """Get user's lab statistics"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_labs = UserLab.objects.filter(user=request.user)

        stats = {
            'total_attempts': user_labs.count(),
            'completed_attempts': user_labs.filter(status='completed').count(),
            'passed_attempts': user_labs.filter(is_passed=True).count(),
            'perfect_scores': user_labs.filter(is_perfect_score=True).count(),
            'total_points_earned': sum(lab.total_points_earned for lab in user_labs),
            'average_score': user_labs.filter(score__isnull=False).aggregate(
                avg_score=models.Avg('score')
            )['avg_score'] or 0,
            'labs_completed': user_labs.filter(is_passed=True).values('lab').distinct().count(),
            'total_time_spent': sum(lab.time_spent or 0 for lab in user_labs.filter(time_spent__isnull=False)),
        }

        # Recent activity
        recent_attempts = user_labs.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')[:5]

        stats['recent_attempts'] = UserLabSerializer(recent_attempts, many=True).data

        return Response(stats)


class ExternalLabResultView(APIView):
    """Endpoint for external lab systems to submit results"""
    permission_classes = []  # External systems will use API keys

    def post(self, request):
        """
        Expected payload from external lab system:
        {
            "redirect_token": "secure_token",
            "external_attempt_id": "ext_123",
            "score": 85,
            "time_spent": 45,
            "notes": "Additional feedback",
            "metadata": {...}
        }
        """
        try:
            data = request.data
            redirect_token = data.get('redirect_token')

            if not redirect_token:
                return Response({'error': 'redirect_token required'}, status=status.HTTP_400_BAD_REQUEST)

            # Find the user lab attempt
            user_lab = UserLab.objects.get(redirect_token=redirect_token)

            # Validate that the session is still active
            if not user_lab.redirect_session.is_valid():
                return Response({'error': 'Session expired or invalid'}, status=status.HTTP_410_GONE)

            # Update the attempt with results
            user_lab.ended_at = timezone.now()
            user_lab.score = data.get('score')
            user_lab.time_spent = data.get('time_spent')
            user_lab.status = 'completed'
            user_lab.external_attempt_id = data.get('external_attempt_id')
            user_lab.notes = data.get('notes', '')

            # Save metadata if provided
            if 'metadata' in data:
                user_lab.notes += f"\nMetadata: {data['metadata']}"

            user_lab.save()  # This triggers point awarding

            # Mark session as used
            user_lab.redirect_session.mark_used()

            logger.info(f"External lab result received: User {user_lab.user.id}, Lab {user_lab.lab.id}, Score {user_lab.score}")

            return Response({
                'success': True,
                'attempt_id': user_lab.id,
                'points_awarded': user_lab.total_points_earned,
                'passed': user_lab.is_passed,
                'return_url': user_lab.redirect_session.return_url
            })

        except UserLab.DoesNotExist:
            return Response({'error': 'Invalid redirect token'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error processing external lab result: {str(e)}")
            return Response({'error': 'Failed to process result'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LabLeaderboardView(APIView):
    """Get lab leaderboard"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, lab_id=None):
        if lab_id:
            # Leaderboard for specific lab
            lab = get_object_or_404(Lab, id=lab_id, status='active')
            attempts = UserLab.objects.filter(
                lab=lab,
                is_passed=True
            ).select_related('user').order_by('-score', 'time_spent')[:10]

            leaderboard = []
            for i, attempt in enumerate(attempts, 1):
                leaderboard.append({
                    'rank': i,
                    'username': attempt.user.username,
                    'score': attempt.score,
                    'time_spent': attempt.time_spent,
                    'perfect_score': attempt.is_perfect_score,
                    'completed_at': attempt.ended_at
                })

            return Response({
                'lab': LabSerializer(lab).data,
                'leaderboard': leaderboard
            })
        else:
            # Overall leaderboard
            from django.db.models import Sum, Count

            top_users = UserLab.objects.filter(
                is_passed=True
            ).values('user__username').annotate(
                total_points=Sum('total_points_earned'),
                labs_completed=Count('lab', distinct=True),
                perfect_scores=Count('id', filter=models.Q(is_perfect_score=True))
            ).order_by('-total_points')[:10]

            return Response({'leaderboard': list(top_users)})
