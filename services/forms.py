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

        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price > max_price:
            self.add_error('min_price', 'Минималната цена не може да е по-голяма от максималната цена!')
            self.add_error('max_price', 'Максималната цена не може да е по-малка от минималната цена!')

        if programmer.services and programmer.services.filter(name=service).exists():
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
