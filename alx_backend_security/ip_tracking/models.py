from django.db import models

class RequestLog(models.Model):
    """
    Model لتخزين كل Request داخل قاعدة البيانات
    """

    # لتخزين عنوان الـ IP (يدعم IPv4 و IPv6)
    ip_address = models.GenericIPAddressField()

    # وقت تنفيذ الريكوست (يتسجل تلقائيًا عند الإنشاء)
    timestamp = models.DateTimeField(auto_now_add=True)

    # المسار المطلوب (مثال: /api/books/)
    path = models.CharField(max_length=255)

    def __str__(self):
        # شكل البيانات عند العرض في Django Admin أو Shell
        return f"{self.ip_address} | {self.path} | {self.timestamp}"

#__________task two: Extend the middleware to block requests from specific IP addresses stored in a BlockedIP model.

class BlockedIP(models.Model):
    """
    جدول لتخزين الـ IPs الممنوعة من الدخول على النظام
    """

    ip_address = models.GenericIPAddressField(unique=True)

    def __str__(self):
        return f"Blocked: {self.ip_address}"

#________________________task 3 : add country and city fields to RequestLog model to store the geolocation information of the ip address making the request.
class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)

    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"{self.ip_address} | {self.path} | {self.timestamp} | {self.country} | {self.city}"
    
#____task 5: Create a SuspiciousIP model to store IP addresses that have exhibited suspicious behavior, along with a reason for suspicion.
from django.db import models

class SuspiciousIP(models.Model):
    """
    نموذج لتخزين الـ IPs المشبوهة مع سبب الاشتباه
    """
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {self.reason}"
    