import os
from celery import Celery
import ssl

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devradar.settings")

app = Celery("devradar")

app.conf.update(
    broker_use_ssl={'ssl_cert_reqs': ssl.CERT_NONE},
    redis_backend_use_ssl={'ssl_cert_reqs': ssl.CERT_NONE},
    broker_transport_options={'ssl': {'ssl_cert_reqs': ssl.CERT_NONE}}
)

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
