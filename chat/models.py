from django.db import models
from django.conf import settings

from core.managers import NonDeletedManager
from moderation.mixins import ViolationSoftDeleteMixin
from moderation.models import BaseReport


class Thread(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    is_deleted = models.BooleanField(default=False)


class Message(ViolationSoftDeleteMixin, models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)




class MessageReport(BaseReport):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reports')
    context_messages = models.ManyToManyField(Message, related_name='message_reports')