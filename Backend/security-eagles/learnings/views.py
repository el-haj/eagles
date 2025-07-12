from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
import django_filters

from .models import (
    Track, LearningPath, LearningSection, UserLearningProgress,
    LearningComment, LearningRating
)
from .serializers import (
    TrackSerializer, LearningPathListSerializer, LearningPathDetailSerializer,
    LearningSectionSerializer, UserLearningProgressSerializer,
    LearningCommentSerializer, LearningRatingSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class TrackFilter(django_filters.FilterSet):
    """Filter for tracks"""
    search = django_filters.CharFilter(method='filter_search')
    category = django_filters.ChoiceFilter(choices=Track.CATEGORY_CHOICES)
    level = django_filters.ChoiceFilter(choices=Track.LEVEL_CHOICES)
    tags = django_filters.CharFilter(method='filter_tags')

    class Meta:
        model = Track
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(tags__overlap=[value])
        )

    def filter_tags(self, queryset, name, value):
        tags = [tag.strip() for tag in value.split(',')]
        return queryset.filter(tags__overlap=tags)


class LearningPathFilter(django_filters.FilterSet):
    """Filter for learning paths"""
    search = django_filters.CharFilter(method='filter_search')
    category = django_filters.ChoiceFilter(choices=Track.CATEGORY_CHOICES)
    level = django_filters.ChoiceFilter(choices=LearningPath.LEVEL_CHOICES)
    tags = django_filters.CharFilter(method='filter_tags')
    is_featured = django_filters.BooleanFilter()
    min_rating = django_filters.NumberFilter(field_name='average_rating', lookup_expr='gte')

    class Meta:
        model = LearningPath
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(short_description__icontains=value) |
            Q(tags__overlap=[value])
        )

    def filter_tags(self, queryset, name, value):
        tags = [tag.strip() for tag in value.split(',')]
        return queryset.filter(tags__overlap=tags)


# Track Views (No Authentication Required)
class TrackListView(generics.ListAPIView):
    """List all active tracks with filtering"""
    serializer_class = TrackSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TrackFilter
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['created_at', 'title', 'download_count', 'duration_hours']
    ordering = ['-created_at']

    def get_queryset(self):
        return Track.objects.filter(is_active=True)


class TrackDetailView(generics.RetrieveAPIView):
    """Get track details and increment download count"""
    serializer_class = TrackSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def get_queryset(self):
        return Track.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment download count
        Track.objects.filter(id=instance.id).update(download_count=F('download_count') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TrackByCategoryView(generics.ListAPIView):
    """Get tracks by category"""
    serializer_class = TrackSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['created_at', 'title', 'download_count', 'duration_hours']
    ordering = ['-created_at']

    def get_queryset(self):
        category = self.kwargs['category']
        return Track.objects.filter(is_active=True, category=category)


# Learning Path Views (Authentication Required)
class LearningPathListView(generics.ListAPIView):
    """List published learning paths with filtering"""
    serializer_class = LearningPathListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = LearningPathFilter
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['created_at', 'title', 'average_rating', 'enrollment_count']
    ordering = ['-is_featured', '-created_at']

    def get_queryset(self):
        return LearningPath.objects.filter(status='published').select_related('instructor')


class LearningPathDetailView(generics.RetrieveAPIView):
    """Get detailed learning path information"""
    serializer_class = LearningPathDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return LearningPath.objects.filter(status='published').select_related('instructor').prefetch_related('sections')


class LearningPathEnrollView(APIView):
    """Enroll in a learning path"""
    permission_classes = [IsAuthenticated]

    def post(self, request, learning_path_id):
        learning_path = get_object_or_404(LearningPath, id=learning_path_id, status='published')

        # Check if already enrolled
        progress, created = UserLearningProgress.objects.get_or_create(
            user=request.user,
            learning_path=learning_path,
            defaults={'status': 'not_started'}
        )

        if created:
            # Increment enrollment count
            LearningPath.objects.filter(id=learning_path_id).update(
                enrollment_count=F('enrollment_count') + 1
            )
            return Response({
                'detail': 'Successfully enrolled in learning path',
                'progress': UserLearningProgressSerializer(progress, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'detail': 'Already enrolled in this learning path',
                'progress': UserLearningProgressSerializer(progress, context={'request': request}).data
            }, status=status.HTTP_200_OK)


class LearningPathUnenrollView(APIView):
    """Unenroll from a learning path"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, learning_path_id):
        try:
            progress = UserLearningProgress.objects.get(
                user=request.user,
                learning_path_id=learning_path_id
            )
            progress.delete()

            # Decrement enrollment count
            LearningPath.objects.filter(id=learning_path_id).update(
                enrollment_count=F('enrollment_count') - 1
            )

            return Response({'detail': 'Successfully unenrolled from learning path'})
        except UserLearningProgress.DoesNotExist:
            return Response(
                {'detail': 'Not enrolled in this learning path'},
                status=status.HTTP_404_NOT_FOUND
            )


class MarkSectionCompleteView(APIView):
    """Mark a learning section as complete"""
    permission_classes = [IsAuthenticated]

    def post(self, request, section_id):
        section = get_object_or_404(LearningSection, id=section_id, is_active=True)

        try:
            progress = UserLearningProgress.objects.get(
                user=request.user,
                learning_path=section.learning_path
            )
        except UserLearningProgress.DoesNotExist:
            return Response(
                {'detail': 'Not enrolled in this learning path'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Add section to completed sections
        progress.completed_sections.add(section)
        progress.current_section = section
        progress.update_progress()

        return Response({
            'detail': 'Section marked as complete',
            'progress': UserLearningProgressSerializer(progress, context={'request': request}).data
        })


class UserLearningProgressListView(generics.ListAPIView):
    """Get user's learning progress"""
    serializer_class = UserLearningProgressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['enrolled_at', 'last_accessed_at', 'progress_percentage']
    ordering = ['-last_accessed_at']

    def get_queryset(self):
        return UserLearningProgress.objects.filter(
            user=self.request.user
        ).select_related('learning_path', 'current_section')


# Comment Views
class LearningCommentListCreateView(generics.ListCreateAPIView):
    """List and create comments for a learning path"""
    serializer_class = LearningCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    ordering = ['-created_at']

    def get_queryset(self):
        learning_path_id = self.kwargs['learning_path_id']
        return LearningComment.objects.filter(
            learning_path_id=learning_path_id,
            is_active=True,
            parent=None  # Only top-level comments
        ).select_related('user')

    def perform_create(self, serializer):
        learning_path_id = self.kwargs['learning_path_id']
        learning_path = get_object_or_404(LearningPath, id=learning_path_id, status='published')
        serializer.save(user=self.request.user, learning_path=learning_path)


class LearningCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a comment"""
    serializer_class = LearningCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LearningComment.objects.filter(is_active=True).select_related('user')

    def perform_update(self, serializer):
        # Only allow owner to update
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You can only edit your own comments")
        serializer.save(is_edited=True)

    def perform_destroy(self, serializer):
        # Only allow owner to delete
        if serializer.user != self.request.user:
            raise PermissionDenied("You can only delete your own comments")
        serializer.is_active = False
        serializer.save()


class LearningCommentRepliesView(generics.ListCreateAPIView):
    """List and create replies to a comment"""
    serializer_class = LearningCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    ordering = ['created_at']

    def get_queryset(self):
        parent_id = self.kwargs['comment_id']
        return LearningComment.objects.filter(
            parent_id=parent_id,
            is_active=True
        ).select_related('user')

    def perform_create(self, serializer):
        parent_comment = get_object_or_404(LearningComment, id=self.kwargs['comment_id'])
        serializer.save(
            user=self.request.user,
            learning_path=parent_comment.learning_path,
            parent=parent_comment
        )


# Rating Views
class LearningRatingListCreateView(generics.ListCreateAPIView):
    """List and create ratings for a learning path"""
    serializer_class = LearningRatingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    ordering = ['-created_at']

    def get_queryset(self):
        learning_path_id = self.kwargs['learning_path_id']
        return LearningRating.objects.filter(
            learning_path_id=learning_path_id
        ).select_related('user')

    def perform_create(self, serializer):
        learning_path_id = self.kwargs['learning_path_id']
        learning_path = get_object_or_404(LearningPath, id=learning_path_id, status='published')

        # Check if user already rated this learning path
        existing_rating = LearningRating.objects.filter(
            user=self.request.user,
            learning_path=learning_path
        ).first()

        if existing_rating:
            # Update existing rating
            for attr, value in serializer.validated_data.items():
                setattr(existing_rating, attr, value)
            existing_rating.save()
            return Response(
                LearningRatingSerializer(existing_rating, context={'request': self.request}).data,
                status=status.HTTP_200_OK
            )
        else:
            # Create new rating
            serializer.save(user=self.request.user, learning_path=learning_path)


class LearningRatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a rating"""
    serializer_class = LearningRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LearningRating.objects.select_related('user', 'learning_path')

    def perform_update(self, serializer):
        # Only allow owner to update
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You can only edit your own ratings")
        serializer.save()

    def perform_destroy(self, serializer):
        # Only allow owner to delete
        if serializer.user != self.request.user:
            raise PermissionDenied("You can only delete your own ratings")
        serializer.delete()
