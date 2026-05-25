from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import models

from django import forms

from accounts.models import DevRadarUser, ProgrammerUser, Ban
from core.mixins import DisableFieldsMixin


class ProgrammerBaseForm(UserCreationForm):
    class Meta:
        model = ProgrammerUser

        fields = ['username', 'first_name', 'last_name', 'image', 'email', 'phone_number']

        labels = {
            'first_name': 'Собствено име',
            'last_name': 'Фамилно име',
            'image': 'Изображение',
            'email': 'Имейл',
            'phone_number': 'Телефонен номер',
        }

        error_messages = {
            'first_name': {
                'required': 'Полето е задължително!'
            },
            'last_name': {
                'required': 'Полето е задължително!'
            },
            'email': {
                'required': 'Полето е задължително!'
            },
            'phone_number': {
                'required': 'Полето е задължително!'
            },
            'image': {
                'required': 'Полето е задължително!'
            }
        }

        help_texts = {
            'first_name': 'Въведете собствено име на програмиста',
            'last_name': 'Въведете фамилно име на програмиста',
            'email': 'Въведете имейл на програмиста',
            'phone_number': 'Въведете телефонен номер на програмиста',
            'image': 'Снимка на програмиста'

        }



class ProgrammerCreationForm(ProgrammerBaseForm):
    pass


class DevRadarUserBaseForm(models.ModelForm):
    class Meta:
        model = get_user_model()

        fields = ['username', 'first_name', 'last_name', 'email']

        labels = {
            'first_name': 'Собствено име',
            'last_name': 'Фамилно име',
            'email': 'Имейл',
        }

        error_messages = {
            'first_name': {
                'required': 'Полето е задължително!'
            },
            'last_name': {
                'required': 'Полето е задължително!'
            },
            'email': {
                'required': 'Полето е задължително!'
            },

        }

        help_texts = {
            'first_name': 'Въведете собствено име',
            'last_name': 'Въведете фамилно име',
            'email': 'Въведете имейл',


        }



class DevRadarUserCreationForm(DevRadarUserBaseForm, UserCreationForm):
    pass

class DevRadarUserUpdateForm(DevRadarUserBaseForm):
    pass

class DevRadarUserDeleteForm(DevRadarUserBaseForm):
    pass

class BaseBanForm(models.ModelForm):
    class Meta:
        model = Ban
        fields = ['reason', 'ban_type', 'permanent', 'duration']

    duration = forms.DurationField(widget=forms.HiddenInput(), required=False)

    years = forms.IntegerField(min_value=0, initial=0, label="Години")
    days = forms.IntegerField(min_value=0, initial=0, label="Дни")
    hours = forms.IntegerField(min_value=0, max_value=23, initial=0, label="Часове")
    minutes = forms.IntegerField(min_value=0, max_value=59, initial=0, label="Минути")


class CreateBanForm(BaseBanForm):

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



class DeleteBanForm(DisableFieldsMixin, BaseBanForm):
    pass