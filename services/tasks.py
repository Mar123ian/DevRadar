from celery import shared_task
from django.core.mail import send_mail

from devradar import settings
from services.models import Service


@shared_task
def send_service_creation_email_task(instance: Service):
        send_mail(
            subject="Успешно добавяне на услуга",
            message=f"Успешно е добавена услугата {instance.name}, предлагана от вас - {instance.programmer.get_full_name()}!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.programmer.email],
        )