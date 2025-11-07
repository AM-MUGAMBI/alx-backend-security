from django.http import HttpResponseForbidden
from django.core.cache import cache
from ipgeolocation import IPGeolocationAPI
from .models import RequestLog, BlockedIP

# Initialize IPGeolocation API
geo_api = IPGeolocationAPI()

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Block if IP is blacklisted
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Access denied: Your IP address has been blocked.")

        # Check cache for geo info
        cache_key = f"geo_{ip}"
        geo_data = cache.get(cache_key)

        if not geo_data:
            try:
                geo_response = geo_api.get_geolocation(ip)
                geo_data = {
                    "country": geo_response.get("country_name", ""),
                    "city": geo_response.get("city", "")
                }
                # Cache for 24 hours (86400 seconds)
                cache.set(cache_key, geo_data, 86400)
            except Exception as e:
                geo_data = {"country": "", "city": ""}
                print(f"Geolocation lookup failed for {ip}: {e}")

        # Log request
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            country=geo_data["country"],
            city=geo_data["city"],
        )

        # Continue with response
        response = self.get_response(request)
        return response
