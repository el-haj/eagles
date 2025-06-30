
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .permissions import ISAdminOrReadOwn
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer

    permission_classes = [permissions.IsAuthenticated,
                          ISAdminOrReadOwn]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        if self.action in ['create']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAdminUser()]  
