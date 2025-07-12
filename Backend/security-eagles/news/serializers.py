from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import News, NewsImage, NewsCategory, NewsComment, NewsLike, NewsView

User = get_user_model()

class NewsCategorySerializer(serializers.ModelSerializer):
    """Serializer for news categories"""
    news_count = serializers.SerializerMethodField()

    class Meta:
        model = NewsCategory
        fields = ['id', 'name', 'slug', 'description', 'color', 'is_active', 'news_count']

    def get_news_count(self, obj):
        return obj.news_articles.filter(status='published').count()

class NewsImageSerializer(serializers.ModelSerializer):
    """Enhanced serializer for news images"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = NewsImage
        fields = ['id', 'image_url', 'caption', 'alt_text', 'is_featured', 'order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

class NewsCommentSerializer(serializers.ModelSerializer):
    """Serializer for news comments"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = NewsComment
        fields = ['id', 'content', 'author_name', 'parent', 'replies', 'reply_count', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return NewsCommentSerializer(obj.replies.filter(is_approved=True), many=True, context=self.context).data
        return []

    def get_reply_count(self, obj):
        return obj.replies.filter(is_approved=True).count()

class NewsPreviewSerializer(serializers.ModelSerializer):
    """Lightweight serializer for news previews/listings"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    featured_image = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='created_by.username', read_only=True)
    reading_time = serializers.ReadOnlyField()
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'subtitle', 'author', 'summary', 'excerpt',
            'category_name', 'category_color', 'tags', 'status', 'priority',
            'is_featured', 'is_breaking', 'published_at', 'created_at',
            'views', 'likes', 'featured_image', 'author_name', 'reading_time',
            'comment_count', 'like_count', 'is_liked_by_user'
        ]

    def get_featured_image(self, obj):
        featured_img = obj.images.filter(is_featured=True).first()
        if not featured_img:
            featured_img = obj.images.first()

        if featured_img:
            return NewsImageSerializer(featured_img, context=self.context).data
        return None

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_like_count(self, obj):
        return obj.user_likes.count()

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_likes.filter(user=request.user).exists()
        return False

class NewsDetailSerializer(serializers.ModelSerializer):
    """Full serializer for complete news article details"""
    category = NewsCategorySerializer(read_only=True)
    images = NewsImageSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='created_by.username', read_only=True)
    reading_time = serializers.ReadOnlyField()
    is_liked_by_user = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'subtitle', 'author', 'summary', 'content',
            'excerpt', 'category', 'tags', 'status', 'priority', 'is_featured',
            'is_breaking', 'published_at', 'created_at', 'updated_at', 'views',
            'likes', 'meta_description', 'meta_keywords', 'images', 'comments',
            'author_name', 'reading_time', 'is_liked_by_user', 'comment_count',
            'like_count'
        ]

    def get_comments(self, obj):
        # Only return top-level comments (no parent)
        top_level_comments = obj.comments.filter(parent=None, is_approved=True).order_by('-created_at')
        return NewsCommentSerializer(top_level_comments, many=True, context=self.context).data

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_likes.filter(user=request.user).exists()
        return False

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_like_count(self, obj):
        return obj.user_likes.count()

class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating news articles"""
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    images = NewsImageSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'subtitle', 'author', 'summary', 'content',
            'category_id', 'tags', 'status', 'priority', 'is_featured',
            'is_breaking', 'meta_description', 'meta_keywords', 'images'
        ]

    def validate_category_id(self, value):
        if value is not None:
            try:
                NewsCategory.objects.get(id=value, is_active=True)
            except NewsCategory.DoesNotExist:
                raise serializers.ValidationError("Invalid category ID or category is not active.")
        return value

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        news = News.objects.create(**validated_data)

        if category_id:
            news.category_id = category_id
            news.save()

        return news

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if category_id is not None:
            instance.category_id = category_id

        instance.save()
        return instance

class NewsAdminSerializer(serializers.ModelSerializer):
    """Admin serializer with all fields for backend management"""
    category = NewsCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    images = NewsImageSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    view_count_today = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'views', 'likes']

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_like_count(self, obj):
        return obj.user_likes.count()

    def get_view_count_today(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        return obj.view_records.filter(created_at__date=today).count()

class NewsImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading news images"""

    class Meta:
        model = NewsImage
        fields = ['image', 'caption', 'alt_text', 'is_featured', 'order']

class NewsCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating news comments"""

    class Meta:
        model = NewsComment
        fields = ['content', 'parent']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['news'] = self.context['news']
        return super().create(validated_data)

class NewsLikeSerializer(serializers.ModelSerializer):
    """Serializer for news likes"""

    class Meta:
        model = NewsLike
        fields = ['created_at']
        read_only_fields = ['created_at']
