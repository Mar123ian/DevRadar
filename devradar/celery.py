import os
import ssl
from celery import Celery

# 1. Задължително в самото начало за Eventlet + psycopg2
try:
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()
except ImportError:
    pass

# 2. Задаване на settings модула
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devradar.settings")

app = Celery("devradar", include=['devradar.tasks', 'services.tasks'])

app.config_from_object("django.conf:settings", namespace="CELERY")

# 3. Импортираме settings ТУК, след като Django е конфигуриран
from django.conf import settings

if getattr(settings, "PRODUCTION", False):
    app.conf.update(
        broker_use_ssl={'ssl_cert_reqs': ssl.CERT_NONE},
        redis_backend_use_ssl={'ssl_cert_reqs': ssl.CERT_NONE},
        broker_transport_options={'ssl': {'ssl_cert_reqs': ssl.CERT_NONE}}
    )

app.autodiscover_tasks()