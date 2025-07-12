from rest_framework import generics, pagination, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, F
from django.http import Http404
from datetime import timedelta

from .models import News, NewsCategory, NewsComment, NewsLike, NewsView
from .serializers import (
    NewsPreviewSerializer, NewsDetailSerializer, NewsCreateUpdateSerializer,
    NewsAdminSerializer, NewsCategorySerializer, NewsCommentSerializer,
    NewsCommentCreateSerializer, NewsLikeSerializer, NewsImageUploadSerializer
)
from core.permissions import IsAdminOrReadOnly

# Custom pagination classes
class NewsPreviewPagination(pagination.PageNumberPagination):
    """Pagination for news previews"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50

class NewsAdminPagination(pagination.PageNumberPagination):
    """Pagination for admin news management"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CommentPagination(pagination.PageNumberPagination):
    """Pagination for comments"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

# Public News Views
class NewsPreviewListView(generics.ListAPIView):
    """
    Endpoint for news previews with pagination and filtering
    Authentication required for all access
    """
    serializer_class = NewsPreviewSerializer
    pagination_class = NewsPreviewPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'summary', 'tags', 'author']
    ordering_fields = ['published_at', 'views', 'likes', 'created_at']
    ordering = ['-published_at']

    def get_queryset(self):
        queryset = News.objects.filter(status='published').select_related('category', 'created_by').prefetch_related('images', 'user_likes', 'comments')

        # Filter by category slug if provided
        category_slug = self.request.query_params.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__overlap=tag_list)

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(published_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(published_at__lte=date_to)

        return queryset

class NewsDetailView(generics.RetrieveAPIView):
    """
    Endpoint for full news article content
    Automatically increments view count
    Authentication required
    """
    serializer_class = NewsDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        return News.objects.filter(status='published').select_related('category', 'created_by').prefetch_related(
            'images', 'comments__author', 'comments__replies__author', 'user_likes'
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Track view
        self._track_view(request, instance)

        # Increment view count
        News.objects.filter(pk=instance.pk).update(views=F('views') + 1)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _track_view(self, request, news):
        """Track individual view for analytics"""
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        NewsView.objects.create(
            news=news,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip_address,
            user_agent=user_agent
        )

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# Category Views
class NewsCategoryListView(generics.ListAPIView):
    """List all active news categories - Authentication required"""
    serializer_class = NewsCategorySerializer
    permission_classes = [IsAuthenticated]
    queryset = NewsCategory.objects.filter(is_active=True)

# Featured and Breaking News Views
class FeaturedNewsListView(generics.ListAPIView):
    """Get featured news articles - Authentication required"""
    serializer_class = NewsPreviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NewsPreviewPagination

    def get_queryset(self):
        return News.objects.filter(
            status='published',
            is_featured=True
        ).select_related('category', 'created_by').prefetch_related('images')

class BreakingNewsListView(generics.ListAPIView):
    """Get breaking news articles - Authentication required"""
    serializer_class = NewsPreviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return News.objects.filter(
            status='published',
            is_breaking=True
        ).select_related('category', 'created_by').prefetch_related('images')[:5]

class LatestNewsListView(generics.ListAPIView):
    """Get latest news from last few days - Authentication required"""
    serializer_class = NewsPreviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NewsPreviewPagination

    def get_queryset(self):
        days_back = int(self.request.query_params.get('days', 7))
        cutoff_date = timezone.now() - timedelta(days=days_back)
        return News.objects.filter(
            status='published',
            published_at__gte=cutoff_date
        ).select_related('category', 'created_by').prefetch_related('images')

# User Interaction Views (Require Authentication)
class NewsLikeToggleView(APIView):
    """Toggle like/unlike for a news article"""
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        news = get_object_or_404(News, slug=slug, status='published')
        like, created = NewsLike.objects.get_or_create(
            news=news,
            user=request.user
        )

        if not created:
            # Unlike - remove the like
            like.delete()
            News.objects.filter(pk=news.pk).update(likes=F('likes') - 1)
            return Response({'liked': False, 'message': 'News unliked'})
        else:
            # Like - increment counter
            News.objects.filter(pk=news.pk).update(likes=F('likes') + 1)
            return Response({'liked': True, 'message': 'News liked'})

class NewsCommentListCreateView(generics.ListCreateAPIView):
    """List and create comments for a news article - Authentication required"""
    serializer_class = NewsCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination

    def get_queryset(self):
        news_slug = self.kwargs['slug']
        news = get_object_or_404(News, slug=news_slug, status='published')
        return news.comments.filter(parent=None, is_approved=True).order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NewsCommentCreateSerializer
        return NewsCommentSerializer

    def perform_create(self, serializer):
        news_slug = self.kwargs['slug']
        news = get_object_or_404(News, slug=news_slug, status='published')
        serializer.save(author=self.request.user, news=news)

# Admin Views (Require Staff/Admin Permissions)
class NewsAdminListCreateView(generics.ListCreateAPIView):
    """Admin endpoint for managing all news articles"""
    serializer_class = NewsAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    pagination_class = NewsAdminPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'published_at', 'views', 'likes']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = News.objects.all().select_related('category', 'created_by').prefetch_related('images')

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by category
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NewsCreateUpdateSerializer
        return NewsAdminSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class NewsAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin endpoint for managing individual news articles"""
    serializer_class = NewsAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        return News.objects.all().select_related('category', 'created_by').prefetch_related('images')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NewsCreateUpdateSerializer
        return NewsAdminSerializer

class NewsPublishToggleView(APIView):
    """Admin endpoint to toggle publish status"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def post(self, request, slug):
        news = get_object_or_404(News, slug=slug)

        if news.status == 'published':
            news.status = 'draft'
            news.published_at = None
        else:
            news.status = 'published'
            if not news.published_at:
                news.published_at = timezone.now()

        news.save()
        serializer = NewsAdminSerializer(news, context={'request': request})
        return Response(serializer.data)

class NewsImageUploadView(APIView):
    """Admin endpoint for uploading news images"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def post(self, request, slug):
        news = get_object_or_404(News, slug=slug)
        serializer = NewsImageUploadSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(news=news)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Analytics Views (Admin Only)
class NewsAnalyticsView(APIView):
    """Admin endpoint for news analytics"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request):
        from django.db.models import Count, Sum

        # Basic stats
        total_news = News.objects.count()
        published_news = News.objects.filter(status='published').count()
        draft_news = News.objects.filter(status='draft').count()
        total_views = News.objects.aggregate(Sum('views'))['views__sum'] or 0
        total_likes = News.objects.aggregate(Sum('likes'))['likes__sum'] or 0

        # Top viewed articles
        top_viewed = News.objects.filter(status='published').order_by('-views')[:10]
        top_viewed_data = NewsPreviewSerializer(top_viewed, many=True, context={'request': request}).data

        # Recent activity
        recent_news = News.objects.order_by('-created_at')[:10]
        recent_data = NewsPreviewSerializer(recent_news, many=True, context={'request': request}).data

        # Category stats
        category_stats = NewsCategory.objects.annotate(
            news_count=Count('news_articles')
        ).values('name', 'news_count')

        return Response({
            'total_news': total_news,
            'published_news': published_news,
            'draft_news': draft_news,
            'total_views': total_views,
            'total_likes': total_likes,
            'top_viewed_articles': top_viewed_data,
            'recent_articles': recent_data,
            'category_stats': list(category_stats)
        })

# Utility Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_search(request):
    """Advanced search endpoint for news articles - Authentication required"""
    query = request.GET.get('q', '')
    if not query:
        return Response({'results': []})

    news_results = News.objects.filter(
        Q(title__icontains=query) |
        Q(summary__icontains=query) |
        Q(content__icontains=query) |
        Q(tags__overlap=[query]),
        status='published'
    ).distinct()[:20]

    serializer = NewsPreviewSerializer(news_results, many=True, context={'request': request})
    return Response({'results': serializer.data})
