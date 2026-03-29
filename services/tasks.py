from celery import shared_task
from django.core.mail import send_mail

from devradar import settings
from services.models import Service


@shared_task
def send_service_creation_email_task(instance_name, instance_programmer_get_full_name, instance_programmer_email):
        send_mail(
            subject="Успешно добавяне на услуга",
            message=f"Успешно е добавена услугата {instance_name}, предлагана от вас - {instance_programmer_get_full_name}!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance_programmer_email],
        )