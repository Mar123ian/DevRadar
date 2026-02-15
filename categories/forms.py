from django import forms

from categories.models import Type, Technology
from core.mixins import DisableFieldsMixin


class TypeForm(forms.ModelForm):


    class Meta:
        model = Type

        fields = ['name', 'description', 'image']

        labels = {
            'name': 'Име',
            'description': 'Описание',
            'image': 'Изображение',
        }

        error_messages = {
            'name': {
                'required': 'Полето е задължително!'
            },
            'description': {
                'required': 'Полето е задължително!'
            },
            'image': {
                'required': 'Полето е задължително!'
            }
        }

        help_texts = {
            'name': 'Въведете име на типа услуга',
            'description': 'Въведете описание на типа услуга',
            'image': 'Изберете изображение за типа услуга',
        }

class CreateTypeForm(TypeForm):
    pass

class DeleteTypeForm(DisableFieldsMixin, TypeForm):
    pass

class TechnologyForm(forms.ModelForm):

    class Meta:
        model = Technology

        fields = ['name', 'image']

        labels = {
            'name': 'Име',
            'image': 'Изображение',
        }

        error_messages = {
            'name': {
                'required': 'Полето е задължително!'
            },
            'image': {
                'required': 'Полето е задължително!'
            }
        }

        help_texts = {
            'name': 'Въведете име на технологията',
            'image': 'Изберете изображение за технологията',
        }

class CreateTechnologyForm(TechnologyForm):
    pass

class DeleteTechnologyForm(DisableFieldsMixin, TechnologyForm):
    pass


