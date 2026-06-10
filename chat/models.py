from django.db import models
from django.conf import settings

from core.managers import NonDeletedManager


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

class MessageReport(models.Model):
    class ReasonChoices(models.TextChoices):
        SPAM = "spam", "Спам"
        HARASSMENT = "harassment", "Тормоз"
        HATE_SPEECH = "hate_speech", "Реч на омразата"
        VIOLENCE = "violence", "Насилие или заплахи"
        SEXUAL_CONTENT = "sexual_content", "Сексуално съдържание"
        SCAM = "scam", "Измама"
        MISINFORMATION = "misinformation", "Дезинформация"
        COPYRIGHT = "copyright", "Нарушение на авторски права"
        OTHER = "other", "Друго"

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(choices=ReasonChoices.choices, default=ReasonChoices.OTHER)
    description = models.TextField(blank=True, null=True)