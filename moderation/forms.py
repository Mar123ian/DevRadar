from moderation.models import Ban
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.forms import models

from django import forms

from core.mixins import DisableFieldsMixin

class BaseBanForm(models.ModelForm):
    class Meta:
        model = Ban
        fields = ['reason', 'ban_type', 'permanent', 'duration']

    duration = forms.DurationField(widget=forms.HiddenInput(), required=False)

    years = forms.IntegerField(min_value=0, initial=0, label="Години")
    days = forms.IntegerField(min_value=0, initial=0, label="Дни")
    hours = forms.IntegerField(min_value=0, max_value=23, initial=0, label="Часове")
    minutes = forms.IntegerField(min_value=0, max_value=59, initial=0, label="Минути")

    def clean(self):
        cleaned_data = super().clean()

        permanent = cleaned_data.get('permanent')

        input_years = cleaned_data.get('years', 0)
        input_days = cleaned_data.get('days', 0)
        input_hours = cleaned_data.get('hours', 0)
        input_minutes = cleaned_data.get('minutes', 0)

        if (input_years == 0 and input_days == 0 and input_hours == 0 and input_minutes == 0) and not permanent:
            raise forms.ValidationError("Моля, въведете времетраене, по-голямо от 0.")

        total_days = input_days + (input_years * 365)

        duration = timedelta(
            days=total_days,
            hours=input_hours,
            minutes=input_minutes
        )

        if permanent and duration:
            raise ValidationError("Не може да има едновременно зададена крайна дата и перманентност!")

        cleaned_data['duration'] = duration


        return cleaned_data


class CreateBanForm(BaseBanForm):
    pass



class DeleteBanForm(DisableFieldsMixin, BaseBanForm):
    pass

class UpdateBanForm(BaseBanForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['ban_type'].widget.attrs['disabled'] = True
        self.fields['ban_type'].required = False

