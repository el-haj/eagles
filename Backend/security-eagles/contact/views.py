from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
import logging

from .models import ContactMessage, ContactSettings
from .serializers import (
    ContactMessageCreateSerializer,
    ContactMessageListSerializer,
    ContactMessageDetailSerializer,
    ContactSettingsSerializer,
    ContactSettingsAdminSerializer
)

logger = logging.getLogger(__name__)


class ContactMessageCreateView(APIView):
    """
    Public API to create contact messages
    No authentication required
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactMessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Get client IP and user agent
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Save the contact message
            contact_message = serializer.save(
                ip_address=ip_address,
                user_agent=user_agent
            )

            # Send auto-response email if enabled
            self.send_auto_response(contact_message)

            # Send admin notification if enabled
            self.send_admin_notification(contact_message)

            return Response({
                'message': 'Your message has been sent successfully! We will get back to you soon.',
                'id': contact_message.id,
                'created_at': contact_message.created_at
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def send_auto_response(self, contact_message):
        """Send automatic response to user"""
        try:
            contact_settings = ContactSettings.objects.first()
            if contact_settings and contact_settings.auto_response_enabled:
                send_mail(
                    subject=f'Thank you for contacting us - {contact_message.get_subject_display()}',
                    message=contact_settings.auto_response_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[contact_message.email],
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Failed to send auto-response: {e}")

    def send_admin_notification(self, contact_message):
        """Send notification to admins"""
        try:
            contact_settings = ContactSettings.objects.first()
            if contact_settings and contact_settings.admin_notification_enabled:
                admin_emails = [
                    email.strip()
                    for email in contact_settings.admin_notification_emails.split(',')
                    if email.strip()
                ]

                if admin_emails:
                    send_mail(
                        subject=f'New Contact Message: {contact_message.get_subject_display()}',
                        message=f"""
New contact message received:

Name: {contact_message.name}
Email: {contact_message.email}
Phone: {contact_message.phone or 'Not provided'}
Company: {contact_message.company or 'Not provided'}
Subject: {contact_message.get_subject_display()}

Message:
{contact_message.message}

Received at: {contact_message.created_at}
IP Address: {contact_message.ip_address}
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=admin_emails,
                        fail_silently=True
                    )
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")


class ContactSettingsView(APIView):
    """
    Public API to get contact settings/information
    No authentication required
    """
    permission_classes = [AllowAny]

    def get(self, request):
        contact_settings = ContactSettings.objects.first()
        if contact_settings:
            serializer = ContactSettingsSerializer(contact_settings)
            return Response(serializer.data)

        # Return empty data if no settings configured
        return Response({
            'community_description': '',
            'contact_email': '',
            'discord_server': '',
            'availability_info': '',
            'website_url': '',
            'github_url': '',
            'twitter_url': '',
            'linkedin_url': '',
            'youtube_url': ''
        })


class ContactSubjectChoicesView(APIView):
    """
    Public API to get available subject choices
    No authentication required
    """
    permission_classes = [AllowAny]

    def get(self, request):
        choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in ContactMessage.SUBJECT_CHOICES
        ]
        return Response(choices)


# Admin Views (Authentication Required)

class ContactMessageListView(generics.ListAPIView):
    """
    Admin API to list all contact messages
    Authentication required
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ContactMessageListSerializer
    queryset = ContactMessage.objects.all()

    def get_queryset(self):
        queryset = ContactMessage.objects.all()

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by subject
        subject_filter = self.request.query_params.get('subject')
        if subject_filter:
            queryset = queryset.filter(subject=subject_filter)

        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')

        # Search in name, email, or message
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(message__icontains=search)
            )

        return queryset.order_by('-created_at')


class ContactMessageDetailView(generics.RetrieveUpdateAPIView):
    """
    Admin API to view and update contact message details
    Authentication required
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ContactMessageDetailSerializer
    queryset = ContactMessage.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Mark as read when viewed
        if not instance.is_read:
            instance.is_read = True
            instance.save(update_fields=['is_read'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ContactSettingsAdminView(APIView):
    """
    Admin API to manage contact settings
    Authentication required
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        contact_settings = ContactSettings.objects.first()
        if contact_settings:
            serializer = ContactSettingsAdminSerializer(contact_settings)
            return Response(serializer.data)

        return Response({}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        # Create or update settings
        contact_settings = ContactSettings.objects.first()

        if contact_settings:
            serializer = ContactSettingsAdminSerializer(contact_settings, data=request.data, partial=True)
        else:
            serializer = ContactSettingsAdminSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactStatsView(APIView):
    """
    Admin API to get contact message statistics
    Authentication required
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        # Total messages
        total_messages = ContactMessage.objects.count()

        # Messages by status
        status_stats = ContactMessage.objects.values('status').annotate(count=Count('id'))

        # Messages by subject
        subject_stats = ContactMessage.objects.values('subject').annotate(count=Count('id'))

        # Recent messages (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_messages = ContactMessage.objects.filter(created_at__gte=week_ago).count()

        # Unread messages
        unread_messages = ContactMessage.objects.filter(is_read=False).count()

        return Response({
            'total_messages': total_messages,
            'unread_messages': unread_messages,
            'recent_messages': recent_messages,
            'status_breakdown': {item['status']: item['count'] for item in status_stats},
            'subject_breakdown': {item['subject']: item['count'] for item in subject_stats}
        })
