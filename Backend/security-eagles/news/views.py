from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status
from .models import News
from .serializers import NewsSerializer
from core.permissions import IsAdminOrReadOnly

class NewsListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]

    def get(self, request):
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10

        news_items = News.objects.filter(is_published=True).order_by('-published_at')[:limit]
        serializer = NewsSerializer(news_items, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = NewsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
