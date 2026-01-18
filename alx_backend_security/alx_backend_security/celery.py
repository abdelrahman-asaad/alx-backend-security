# alx_backend_security/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# 1️⃣ تحديد إعدادات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_security.settings')

# 2️⃣ تهيئة Celery
app = Celery('alx_backend_security')

# قراءة إعدادات Celery من settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# اكتشاف المهام في كل التطبيقات تلقائيًا
app.autodiscover_tasks()

# 3️⃣ Beat Schedule لتشغيل المهمة detect_suspicious_ips كل ساعة
app.conf.beat_schedule = {
    'detect-suspicious-ips-every-hour': {
        'task': 'ip_tracking.tasks.detect_suspicious_ips',
        'schedule': crontab(minute=0),  # كل ساعة على رأس الساعة
        'options': {'queue': 'default'}, # اختياري، لو عايز تحدد Queue
    },
}
