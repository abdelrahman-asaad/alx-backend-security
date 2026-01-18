from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP
from django.db.models import Count

@shared_task
def detect_suspicious_ips():
    """
    Task يتم تشغيلها كل ساعة
    - ترصد الـ IPs التي تجاوزت 100 request/hour
    - أو التي وصلت لمسارات حساسة (/admin, /login)
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # 1️⃣ IPs التي تجاوزت 100 request
    high_traffic_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(count=Count('id'))
        .filter(count__gt=100)                         #count__gt means count greater than 100
    )

    for item in high_traffic_ips:
        ip = item['ip_address']
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            reason=f"High traffic: {item['count']} requests/hour"
        )

    # 2️⃣ IPs التي وصلت لمسارات حساسة
    sensitive_paths = ['/admin', '/login']
    suspicious_requests = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago, path__in=sensitive_paths)
        .values('ip_address', 'path')
    )

    for req in suspicious_requests:
        ip = req['ip_address']
        path = req['path']
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            reason=f"Accessed sensitive path: {path}"
        )
