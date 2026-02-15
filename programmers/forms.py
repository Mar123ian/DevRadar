from django import forms

from core.mixins import DisableFieldsMixin
from programmers.models import Programmer


class ProgrammerForm(forms.ModelForm):
    model = Programmer
    fields = ['first_name', 'last_name', 'email', 'phone_number']

    class Meta:
        labels = {
            'first_name': 'Собствено име',
            'last_name': 'Фамилно име',
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
            }
        }

        help_texts = {
            'name': 'Въведете име на типа услуга',
            'description': 'Въведете описание на типа услуга',
            'image': 'Изберете изображение за типа услуга',
        }

class CreateProgrammerForm(ProgrammerForm):
    pass

class DeleteProgrammerForm(DisableFieldsMixin, ProgrammerForm):
    pass