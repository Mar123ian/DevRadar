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

class ReportedMessage(models.Model):
    ...

class ReportedService(models.Model):
    ...

class ReportedComment(models.Model):
    ...





