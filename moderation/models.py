from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

#TODO better soft del names


# Create your models here.
class Ban(models.Model):
    class BanType(models.TextChoices):
        CHAT_BAN = 'CHAT_BAN', 'Chat ban'
        COMMENTS_BAN = 'COMMENTS_BAN', 'Comments ban'
        OFFER_SERVICE_BAN = 'OFFER_SERVICE_BAN', 'Offer service ban'
        FULL_BAN = 'FULL_BAN', 'Full ban'

    user = models.ForeignKey('accounts.DevRadarUser', on_delete=models.CASCADE, related_name='bans')
    reason = models.CharField(max_length=150, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(blank=True)
    permanent = models.BooleanField(default=False)


    ban_type = models.CharField(
        max_length=20,
        choices=BanType.choices,
        default=BanType.FULL_BAN,
    )

from django.db import models
from django.conf import settings

class BaseReport(models.Model):
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

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(choices=ReasonChoices.choices, default=ReasonChoices.OTHER)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True





