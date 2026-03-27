from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import models

from accounts.models import DevRadarUser, ProgrammerUser


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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if DevRadarUser.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email

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

    #TODO review this
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if DevRadarUser.objects.filter(email=email).exists():
    #         raise ValidationError("Email already exists.")
    #     return email

class DevRadarUserCreationForm(UserCreationForm, DevRadarUserBaseForm):
    pass

class DevRadarUserUpdateForm(DevRadarUserBaseForm):
    pass

class DevRadarUserDeleteForm(DevRadarUserBaseForm):
    pass