from django.db import models
from django.conf import settings

from core.managers import NonDeletedManager
from moderation.models import BaseReport


class Thread(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    is_deleted = models.BooleanField(default=False)


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedManager()
    all_objects = models.Manager()

class MessageReport(BaseReport):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)