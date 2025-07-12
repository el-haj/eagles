from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from .models import News, NewsImage, NewsCategory, NewsComment, NewsLike, NewsView

class NewsImageInline(admin.TabularInline):
    """Inline admin for news images"""
    model = NewsImage
    extra = 1
    fields = ('image', 'caption', 'alt_text', 'is_featured', 'order')
    readonly_fields = ('created_at',)

class NewsCommentInline(admin.TabularInline):
    """Inline admin for news comments"""
    model = NewsComment
    extra = 0
    fields = ('author', 'content', 'is_approved', 'created_at')
    readonly_fields = ('author', 'created_at')
    can_delete = True

@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    """Admin interface for news categories"""
    list_display = ('name', 'slug', 'color_display', 'is_active', 'news_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'

    def news_count(self, obj):
        return obj.news_articles.count()
    news_count.short_description = 'Articles Count'

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Enhanced admin interface for news articles"""
    list_display = (
        'title', 'author', 'category', 'status_display', 'priority_display',
        'is_featured', 'is_breaking', 'views', 'likes', 'published_at', 'created_by'
    )
    list_filter = (
        'status', 'priority', 'category', 'is_featured', 'is_breaking',
        'published_at', 'created_at'
    )
    search_fields = ('title', 'author', 'summary', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = (
        'created_by', 'created_at', 'updated_at', 'views', 'likes',
        'reading_time', 'view_link'
    )
    inlines = [NewsImageInline, NewsCommentInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'subtitle', 'author', 'category')
        }),
        ('Content', {
            'fields': ('summary', 'content', 'excerpt'),
            'classes': ('wide',)
        }),
        ('Publishing', {
            'fields': ('status', 'priority', 'is_featured', 'is_breaking', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Categorization', {
            'fields': ('tags',),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views', 'likes', 'reading_time'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at', 'view_link'),
            'classes': ('collapse',)
        }),
    )

    actions = ['publish_articles', 'unpublish_articles', 'feature_articles', 'unfeature_articles']

    def status_display(self, obj):
        colors = {
            'draft': '#6c757d',
            'review': '#ffc107',
            'published': '#28a745',
            'archived': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def priority_display(self, obj):
        colors = {
            'low': '#17a2b8',
            'normal': '#6c757d',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'

    def view_link(self, obj):
        if obj.pk and obj.status == 'published':
            url = reverse('news:detail', kwargs={'slug': obj.slug})
            return format_html('<a href="{}" target="_blank">View Article</a>', url)
        return "Not published"
    view_link.short_description = 'Public Link'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user

        # Auto-set published_at when status changes to published
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()

        super().save_model(request, obj, form, change)

    # Custom admin actions
    def publish_articles(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} articles were successfully published.')
    publish_articles.short_description = "Publish selected articles"

    def unpublish_articles(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} articles were unpublished.')
    unpublish_articles.short_description = "Unpublish selected articles"

    def feature_articles(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} articles were featured.')
    feature_articles.short_description = "Feature selected articles"

    def unfeature_articles(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} articles were unfeatured.')
    unfeature_articles.short_description = "Unfeature selected articles"

@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    """Admin interface for news comments"""
    list_display = ('news_title', 'author', 'content_preview', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'news__category')
    search_fields = ('content', 'author__username', 'news__title')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_comments', 'disapprove_comments']

    def news_title(self, obj):
        return obj.news.title[:50] + "..." if len(obj.news.title) > 50 else obj.news.title
    news_title.short_description = 'News Article'

    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Comment'

    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments were approved.')
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments were disapproved.')
    disapprove_comments.short_description = "Disapprove selected comments"

@admin.register(NewsLike)
class NewsLikeAdmin(admin.ModelAdmin):
    """Admin interface for news likes"""
    list_display = ('news_title', 'user', 'created_at')
    list_filter = ('created_at', 'news__category')
    search_fields = ('news__title', 'user__username')
    readonly_fields = ('created_at',)

    def news_title(self, obj):
        return obj.news.title[:50] + "..." if len(obj.news.title) > 50 else obj.news.title
    news_title.short_description = 'News Article'

@admin.register(NewsView)
class NewsViewAdmin(admin.ModelAdmin):
    """Admin interface for news views (analytics)"""
    list_display = ('news_title', 'user_display', 'ip_address', 'created_at')
    list_filter = ('created_at', 'news__category')
    search_fields = ('news__title', 'user__username', 'ip_address')
    readonly_fields = ('created_at',)

    def news_title(self, obj):
        return obj.news.title[:50] + "..." if len(obj.news.title) > 50 else obj.news.title
    news_title.short_description = 'News Article'

    def user_display(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    user_display.short_description = 'User'

    def has_add_permission(self, request):
        return False  # Don't allow manual creation of view records

    def has_change_permission(self, request, obj=None):
        return False  # Don't allow editing of view records
