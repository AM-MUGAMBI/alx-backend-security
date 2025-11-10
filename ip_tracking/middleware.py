import logging
from django.utils import timezone
from ipgeolocation import IPGeolocation
from django.core.cache import cache
from .models import RequestLog

logger = logging.getLogger(__name__)
geo = IPGeolocation()

class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.log_request(request)
        return response

    def log_request(self, request):
        ip = self.get_client_ip(request)
        if not ip:
            return

        # Cache key for 24 hours
        cache_key = f"geo_{ip}"
        geo_data = cache.get(cache_key)

        if not geo_data:
            try:
                geo_info = geo.lookup(ip)
                geo_data = {
                    'country': geo_info.get('country_name', ''),
                    'city': geo_info.get('city', ''),
                }
                cache.set(cache_key, geo_data, 60 * 60 * 24)  # 24 hours
            except Exception as e:
                logger.warning(f"Geo lookup failed for {ip}: {e}")
                geo_data = {'country': '', 'city': ''}

        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            method=request.method,
            timestamp=timezone.now(),
            country=geo_data['country'],
            city=geo_data['city'],
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
