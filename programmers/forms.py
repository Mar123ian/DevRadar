from django import forms

from core.mixins import DisableFieldsMixin
from programmers.models import Programmer


class ProgrammerForm(forms.ModelForm):


    class Meta:
        model = Programmer

        fields = ['first_name', 'last_name', 'image', 'email', 'phone_number']

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

class CreateProgrammerForm(ProgrammerForm):
    pass

class UpdateProgrammerForm(ProgrammerForm):
    pass

class DeleteProgrammerForm(DisableFieldsMixin, ProgrammerForm):
    pass