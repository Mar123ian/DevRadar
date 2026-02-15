from django import forms

from core.mixins import DisableFieldsMixin
from services.models import Service


class ServiceForm(forms.ModelForm):
    model = Service
    fields = ['name', 'programmer', 'description', 'image', 'type', 'technologies', 'min_price', 'max_price']

    class Meta:
        labels = {
            'name': 'Име',
            'programmer': 'Програмист',
            'description': 'Описание',
            'image': 'Изображение',
            'type': 'Тип',
            'technologies': 'Технологии',
            'min_price': 'Минимална цена',
            'max_price': 'Максимална цена'

        }

        error_messages = {
            'name': {
                'required': 'Полето е задължително!'
            },
            'programmer': {
                'required': 'Полето е задължително!'
            },
            'description': {
                'required': 'Полето е задължително!'
            },
            'image': {
                'required': 'Полето е задължително!'
            },
            'type': {
                'required': 'Полето е задължително!'
            },
            'technologies': {
                'required': 'Полето е задължително!'
            },
            'min_price': {
                'required': 'Полето е задължително!'
            },
            'max_price': {
                'required': 'Полето е задължително!'
            }
        }

        help_texts = {
            'name': 'Въведете заглавие на услугата',
            'programmer': 'Изберете програмиста, предлагащ услугата',
            'description': 'Въведете описание на услугата',
            'image': 'Изберете изображение за услугата',
            'type': 'Изберете типа на услугата',
            'technologies': 'Изберете технологиите, които ще се ползват',
            'min_price': 'Въведете минимална цена',
            'max_price': 'Въведете максимална цена'

        }

    def clean(self):
        cleaned_data = super().clean()
        programmer = cleaned_data.get('programmer')
        service = cleaned_data.get('service')

        if programmer.services.filter(id=service.id).exists():
            self.add_error('service',"Този програмист вече е предложил същата услуга!")
            
        return cleaned_data


class CreateServiceForm(ServiceForm):
    pass

class DeleteServiceForm(DisableFieldsMixin, ServiceForm):
    pass