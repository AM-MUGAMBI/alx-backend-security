from .models import RequestLog
from datetime import datetime

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Log the request details
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
        )

        # Continue processing the request
        response = self.get_response(request)
        return response
