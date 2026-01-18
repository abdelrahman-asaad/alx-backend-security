from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit

# ✅ Login view فقط للـ Rate Limiting
@ratelimit(key='user_or_ip', rate='10/m', method='POST', block=False)  # 10 requests/min للمستخدمين المسجلين، أو IP للمجهولين
@ratelimit(key='ip', rate='5/m', method='POST', block=False)           # 5 requests/min لكل IP
def login_view(request):
    """
    Login view محمي فقط بالـ Rate Limiting.
    باقي العمليات (Blacklist, Logging, Geolocation) موجودة في Middleware.
    """

    # تحقق إذا تجاوز الحد
    if getattr(request, 'limited', False):
        return HttpResponse("Too many requests", status=429)

    # لو الحد لم يتم تجاوزه، نرجع رسالة بسيطة أو صفحة Login
    return HttpResponse("Login page - request allowed ✅")
