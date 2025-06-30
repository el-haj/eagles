# events/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .models import Event, EventRegistration
from .serializers import EventSerializer

class EventListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = request.user
        events = Event.objects.filter(is_active=True).order_by('start_time')

        registered_ids = []
        if user.is_authenticated:
            registered_ids = list(EventRegistration.objects.filter(user=user, is_canceled=False).values_list('event_id', flat=True))

        serializer = EventSerializer(events, many=True, context={'request': request})
        data = serializer.data

        # Add registration status for each event
        for event in data:
            event['is_registered'] = event['id'] in registered_ids

        return Response(data)

    def post(self, request):
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventRegisterView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, event_id):
        user = request.user
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        registration, created = EventRegistration.objects.get_or_create(user=user, event=event)
        if created:
            return Response({'detail': 'Registered successfully.'})
        elif registration.is_canceled:
            registration.is_canceled = False
            registration.save()
            return Response({'detail': 'Re-registered successfully.'})
        else:
            return Response({'detail': 'Already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id):
        user = request.user
        try:
            registration = EventRegistration.objects.get(user=user, event_id=event_id, is_canceled=False)
            registration.is_canceled = True
            registration.save()
            return Response({'detail': 'Unregistered successfully.'})
        except EventRegistration.DoesNotExist:
            return Response({'detail': 'Registration not found.'}, status=status.HTTP_404_NOT_FOUND)
