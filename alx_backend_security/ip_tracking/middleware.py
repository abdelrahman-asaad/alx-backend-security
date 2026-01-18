#task one: Create a middleware that logs the IP address, path, and time of each request into the database.
from .models import RequestLog

class IPLoggingMiddleware:
    """
    Middleware مسؤولة عن تسجيل:
    - IP Address
    - Path
    - Time لكل Request داخل النظام
    """

    def __init__(self, get_response):
        # Django بيمرر دالة تنفيذ الـ View هنا مرة واحدة عند تشغيل السيرفر
        self.get_response = get_response

    def __call__(self, request):
        # هذه الدالة تُنفّذ مع كل Request

        # 1️⃣ محاولة الحصول على IP الحقيقي في حالة وجود Proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR') #in case of proxy and load balancers , X-Forwarded-For: 41.33.10.5, 10.0.0.2 here we take the first one 41 as client ip


        if x_forwarded_for:
            # في حالة وجود أكثر من IP، نأخذ أول واحد (العميل الحقيقي)
            ip = x_forwarded_for.split(',')[0]            #get the first ip from the list of ips in case of multiple ips in x-forwarded-for header
        else:
            # IP المباشر من السيرفر
            ip = request.META.get('REMOTE_ADDR') # in case of direct request from client without proxy

        # 2️⃣ حفظ البيانات داخل قاعدة البيانات
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path  # المسار الذي تم طلبه
        )

        # 3️⃣ تمرير الطلب لباقي الـ Middlewares ثم الـ View
        response = self.get_response(request)

        # 4️⃣ إعادة الـ Response للعميل
        return response

# this is middleware to log ip address, path and time of each request into database which is not in real world application because logging each request into database will slow down the application performance but it is useful for learning purposes and understanding how middleware works in django
# we must log them in real world application using logging services like redis, elasticsearch, logstash, kibana etc.
# we add this middleware to settings.py file in MIDDLEWARE list to activate it
#____________________________
#task two: Extend the middleware to block requests from specific IP addresses stored in a BlockedIP model.
from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP

class IPLoggingMiddleware:
    """
    Middleware مسؤولة عن:
    - تسجيل الطلبات
    - منع الـ IPs المحظورة
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # استخراج IP الحقيقي
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # 1️⃣ التحقق هل الـ IP محظور؟
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # 2️⃣ تسجيل الطلب لو غير محظور
        RequestLog.objects.create(              #log the request if not blocked in the database RequestLog table
            ip_address=ip,
            path=request.path
        )

        return self.get_response(request)
#___________________________________
# task 3 : add country and city fields to RequestLog model to store the geolocation information of the 
# ip address making the request.

from django.http import HttpResponseForbidden
from django.core.cache import cache
from .models import RequestLog, BlockedIP

from ipgeolocation import IpGeolocationAPI

class IPLoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # تهيئة كائن الـ API مرة واحدة
        self.geo_api = IpGeolocationAPI()  #geo_api is an instance of IpGeolocationAPI class to get the geolocation data of the ip address

    def get_client_ip(self, request):
        """استخراج IP الحقيقي"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def get_geo_data(self, ip):
        """
        إرجاع الدولة والمدينة مع Cache لمدة 24 ساعة
        """
        cache_key = f"geo_{ip}"
        cached = cache.get(cache_key)

        if cached:
            return cached

        # استدعاء API
        result = self.geo_api.get_location(ip)

        country = result.get("country_name")
        city = result.get("city")

        data = {"country": country, "city": city}

        # تخزين في الكاش لمدة 24 ساعة
        cache.set(cache_key, data, 60 * 60 * 24)
        return data

    def __call__(self, request):  #call method is called for each request

        ip = self.get_client_ip(request)

        # منع الـ IP المحظور
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # الحصول على الموقع الجغرافي
        geo = self.get_geo_data(ip)

        # تسجيل الطلب log the request with geolocation data in the database
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            country=geo.get("country"),
            city=geo.get("city"),
        )

        return self.get_response(request)
