from rest_framework import serializers
from .models import LearningPath, LearningPDF, UserLearning

class LearningPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPDF
        fields = '__all__'

class LearningPathSerializer(serializers.ModelSerializer):
    pdfs = LearningPDFSerializer(many=True, read_only=True)

    class Meta:
        model = LearningPath
        fields = '__all__'

class UserLearningSerializer(serializers.ModelSerializer):
    learning_path = LearningPathSerializer(read_only=True)
    learning_path_id = serializers.PrimaryKeyRelatedField(
        queryset=LearningPath.objects.all(), source='learning_path', write_only=True
    )
    pdf = LearningPDFSerializer(read_only=True)
    pdf_id = serializers.PrimaryKeyRelatedField(
        queryset=LearningPDF.objects.all(), source='pdf', write_only=True, required=False
    )

    class Meta:
        model = UserLearning
        fields = '__all__'
        
        
class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = '__all__'
