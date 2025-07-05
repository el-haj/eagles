from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status
from .models import Certification
from .serializers import CertificationListSerializer, CertificationDetailSerializer

class CertificationListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly,IsAuthenticated]

    def get(self, request):
        certifications = Certification.objects.filter(is_active=True).order_by('-created_at')
        serializer = CertificationListSerializer(certifications, many=True, context={'request': request})
        if not certifications.exists():
            return Response({'detail': 'No certifications found.'}, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CertificationDetailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CertificationDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly,IsAuthenticated]

    def get(self, request, pk):
        try:
            certification = Certification.objects.get(pk=pk, is_active=True)
        except Certification.DoesNotExist:
            return Response({'detail': 'Certification not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CertificationDetailSerializer(certification, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            certification = Certification.objects.get(pk=pk)
        except Certification.DoesNotExist:
            return Response({'detail': 'Certification not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CertificationDetailSerializer(certification, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            certification = Certification.objects.get(pk=pk)
        except Certification.DoesNotExist:
            return Response({'detail': 'Certification not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not certification.is_active:
            return Response({'detail': 'Certification already deactivated.'}, status=status.HTTP_400_BAD_REQUEST)
        certification.is_active = False
        certification.save()
        return Response({'detail': 'Certification deactivated.'}, status=status.HTTP_200_OK)

class CertificationActivateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly,IsAuthenticated]

    def post(self, request, pk):
        try:
            certification = Certification.objects.get(pk=pk)
        except Certification.DoesNotExist:
            return Response({'detail': 'Certification not found.'}, status=status.HTTP_404_NOT_FOUND)
        if certification.is_active:
            return Response({'detail': 'Certification is already active.'}, status=status.HTTP_400_BAD_REQUEST)
        certification.is_active = True
        certification.save()
        return Response({'detail': 'Certification activated.'}, status=status.HTTP_200_OK)