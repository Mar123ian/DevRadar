import os
from celery import Celery

# 1. Пач за съвместимост между Eventlet и psycopg2
try:
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()
except ImportError:
    pass

# 2. Инициализация на Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devradar.settings")

app = Celery("devradar", include=['devradar.tasks', 'services.tasks'])
app.config_from_object("django.conf:settings", namespace="CELERY")

# 3. Активираме SSL САМО ако URL адресът започва с 'rediss://'
from django.conf import settings
broker_url = getattr(settings, 'CELERY_BROKER_URL', '') or getattr(settings, 'REDIS_URL', '')

if broker_url.startswith('rediss://'):
    import ssl
    app.conf.update(
        broker_use_ssl={'ssl_cert_reqs': ssl.CERT_NONE},
        redis_backend_use_ssl={'ssl_cert_reqs': ssl.CERT_NONE},
        broker_transport_options={'ssl': {'ssl_cert_reqs': ssl.CERT_NONE}}
    )

app.autodiscover_tasks()