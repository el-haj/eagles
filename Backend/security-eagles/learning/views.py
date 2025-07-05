from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import LearningPath, UserLearning
from .serializers import LearningPathSerializer, UserLearningSerializer


class LearningPathListCreateView(generics.ListCreateAPIView):
    queryset = LearningPath.objects.all().order_by('-created_at')
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class UserLearningListCreateView(generics.ListCreateAPIView):
    serializer_class = UserLearningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserLearning.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserLearningUpdateView(generics.UpdateAPIView):
    serializer_class = UserLearningSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return UserLearning.objects.filter(user=self.request.user)
