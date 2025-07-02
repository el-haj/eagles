from rest_framework import generics, permissions
from .models import Lab, UserLab
from .serializers import LabSerializer, UserLabSerializer

class LabListView(generics.ListAPIView):
    queryset = Lab.objects.all().order_by('-created_at')
    serializer_class = LabSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class LabDetailView(generics.RetrieveAPIView):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserLabCreateView(generics.CreateAPIView):
    queryset = UserLab.objects.all()
    serializer_class = UserLabSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserLabListView(generics.ListAPIView):
    serializer_class = UserLabSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserLab.objects.filter(user=self.request.user).order_by('-created_at')
