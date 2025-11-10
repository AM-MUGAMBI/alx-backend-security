from django.db import models

class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    # New fields for geolocation
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.ip_address} - {self.path}"
