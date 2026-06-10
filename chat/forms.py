from django.forms import models

from chat.models import MessageReport


class MessageReportForm(models.ModelForm):
    class Meta:
        model = MessageReport
        fields = ['reason', 'description']