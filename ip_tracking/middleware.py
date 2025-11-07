from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Check if the IP is blocked
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Access denied: Your IP address has been blocked.")

        # Log request if not blocked
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
        )

        response = self.get_response(request)
        return response
