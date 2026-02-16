from django import forms

from categories.models import Type, Technology
from core.mixins import DisableFieldsMixin
from services.models import Service


class ServiceForm(forms.ModelForm):

    class Meta:
        model = Service

        fields = ['name', 'programmer', 'description', 'image', 'type', 'technologies', 'min_price', 'max_price']

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

class SearchSortAndFilterServicesForm(forms.Form):
    search_query = forms.CharField(required=False, max_length=255, error_messages={'max_length': 'Максималната дължина е 255 символа!'})
    type = forms.ModelChoiceField(queryset=Type.objects.all(), required=False)
    technologies = forms.ModelMultipleChoiceField(queryset=Technology.objects.all(), required=False)
    min_price = forms.DecimalField(required=False, decimal_places=2, max_digits=10, error_messages={'max_digits': 'Максималната дължина е 10 цифри!', 'decimal_places': 'Максималната дължина след десетичната запетая е 2 цифри!'})
    max_price = forms.DecimalField(required=False, decimal_places=2, max_digits=10, error_messages={'max_digits': 'Максималната дължина е 10 цифри!', 'decimal_places': 'Максималната дължина след десетичната запетая е 2 цифри!'})
    desc_price = forms.BooleanField(required=False, initial=False)
