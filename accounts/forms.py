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