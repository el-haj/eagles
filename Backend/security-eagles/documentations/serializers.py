from rest_framework import serializers
from .models import Documentation

class DocumentationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documentation
        fields = ['id', 'title','name', 'category', 'description']  # summary fields

class DocumentationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documentation
        fields = '__all__'  # all fields