from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            'error': True,
            'details': response.data,
        }, status=response.status_code)

    # For non-DRF exceptions
    return Response({
        'error': True,
        'details': str(exc),
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.http import JsonResponse

def custom_404(request, exception):
    return JsonResponse({"error": True, "details": "Not Found"}, status=404)

def custom_500(request):
    return JsonResponse({"error": True, "details": "Server Error"}, status=500)

def custom_403(request, exception):
    return JsonResponse({"error": True, "details": "Forbidden"}, status=403)

def custom_csrf_failure(request, reason=""):
    return JsonResponse({"error": True, "details": f"CSRF Failed: {reason}"}, status=403)
