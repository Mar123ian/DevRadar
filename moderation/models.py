from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError
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
    active = models.BooleanField(default=True)


    ban_type = models.CharField(
        max_length=20,
        choices=BanType.choices,
        default=BanType.FULL_BAN,
    )

    def is_active(self):
        if self.active and self.permanent:
            return True
        if self.active and self.duration:
            return self.start_date + self.duration > timezone.now()
        return False

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

class BaseAppeal(models.Model):
    description = models.TextField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError:
            # 1. Взимаме точния клас на настоящия обект (ServiceAppeal, CommentAppeal и т.н.)
            model_class = self._meta.model

            # 2. Изтриваме стария запис
            # (За ServiceAppeal търси по self.service, за CommentAppeal - по self.comment и т.н.)
            if hasattr(self, 'service'):
                model_class.objects.filter(service=self.service).delete()
            elif hasattr(self, 'comment'):
                model_class.objects.filter(comment=self.comment).delete()
            elif hasattr(self, 'message'):
                model_class.objects.filter(message=self.message).delete()

            # 3. Записваме новия обект наново
            super().save(*args, **kwargs)


class BanAppeal(BaseAppeal):
    ban = models.OneToOneField(Ban, on_delete=models.CASCADE, related_name='violation_appeal')





