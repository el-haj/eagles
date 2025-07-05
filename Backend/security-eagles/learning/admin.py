from django.contrib import admin
from .models import LearningPath, LearningPDF, UserLearning

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'estimated_time', 'created_by', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'objectives', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('created_by',)

@admin.register(LearningPDF)
class LearningPDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'learning_path', 'order_index', 'page_count', 'uploaded_at')
    list_filter = ('learning_path',)
    search_fields = ('learning_path__title',)
    readonly_fields = ('uploaded_at',)

@admin.register(UserLearning)
class UserLearningAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'learning_path', 'pdf', 'page', 'completion', 'created_at', 'updated_at')
    list_filter = ('learning_path', 'user')
    search_fields = ('learning_path__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('user', 'learning_path', 'pdf')

    def display_tags(self, obj):
        return ", ".join(obj.tags)
    display_tags.short_description = "Tags"