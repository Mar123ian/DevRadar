from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
import services
from devradar import settings
from services.models import Service
from services.tasks import send_service_creation_email_task


@receiver(post_save, sender=Service)
def send_service_creation_email(sender, instance: Service, created, **kwargs):
    if created:
        send_service_creation_email_task(sender)