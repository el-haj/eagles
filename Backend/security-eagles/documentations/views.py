# events/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status
from .models import Documentation
from .serializers import DocumentationDetailSerializer,DocumentationListSerializer

class DocumentationView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly,IsAuthenticated]

    def get(self,request):
        Documentations = Documentation.objects.filter(is_active=True).order_by('created_at')
        serializer = DocumentationListSerializer(Documentations, many=True, context={'request': request})
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self, request):
        serializer = DocumentationDetailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DocumentationDetailView(APIView):
   permission_classes = [IsAuthenticatedOrReadOnly,IsAuthenticated]
   def get(self, request,pk):
        try:
         documentation = Documentation.objects.get(is_active=True,pk=pk)
        except Documentation.DoesNotExist:
         return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentationDetailSerializer(documentation)
        return Response(serializer.data,status=status.HTTP_200_OK)
   def put(self, request, pk):
        try:
            documentation = Documentation.objects.get(pk=pk)
        except Documentation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentationDetailSerializer(documentation, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   def delete(self, request, pk):
    try:
        documentation = Documentation.objects.get(pk=pk)
    except Documentation.DoesNotExist:
        return Response({'detail': 'Documentation not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if not documentation.is_active:
        return Response({'detail': 'Documentation is already deactivated.'}, status=status.HTTP_400_BAD_REQUEST)
    
    documentation.is_active = False
    documentation.save()
    return Response({'detail': 'Documentation deactivated (soft deleted).'}, status=status.HTTP_200_OK)


#to activate a doc
class DocumentationActivateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly,IsAuthenticated]

    def post(self, request, pk):
        try:
            documentation = Documentation.objects.get(pk=pk)
        except Documentation.DoesNotExist:
            return Response({'detail': 'Documentation not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if documentation.is_active:
            return Response({'detail': 'Documentation is already active.'}, status=status.HTTP_400_BAD_REQUEST)
        
        documentation.is_active = True
        documentation.save()
        return Response({'detail': 'Documentation activated.'}, status=status.HTTP_200_OK)