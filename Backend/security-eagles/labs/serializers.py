from rest_framework import serializers
from .models import Lab, UserLab

class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = '__all__'

class UserLabSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLab
        fields = '__all__'
