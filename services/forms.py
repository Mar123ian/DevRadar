from django import forms
from django.db import models

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


        widgets = {
            'technologies': forms.CheckboxSelectMultiple(),
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

class UpdateServiceForm(ServiceForm):
    pass

class DeleteServiceForm(DisableFieldsMixin, ServiceForm):
    pass

class SearchSortAndFilterServicesForm(forms.Form):

    class PerPageChoices(models.IntegerChoices):
        FIVE = 5, '5'
        TEN = 10, '10'
        THIRTY = 30, '30'
        ONE_HUNDRED = 100, '100'


    search_query = forms.CharField(label='Търси по заглавие', required=False, max_length=255, error_messages={'max_length': 'Максималната дължина е 255 символа!'})
    type = forms.ModelChoiceField(label='Тип услуга', queryset=Type.objects.all(), required=False)
    technologies = forms.ModelMultipleChoiceField(label='Използвани технологии', queryset=Technology.objects.all(), required=False, widget=forms.CheckboxSelectMultiple())
    min_price = forms.DecimalField(label='Минимална цена', min_value=0, required=False, decimal_places=2, max_digits=10, error_messages={'max_digits': 'Максималната дължина е 10 цифри!', 'decimal_places': 'Максималната дължина след десетичната запетая е 2 цифри!', 'min_value': 'Минималната цена е 0€!'})
    max_price = forms.DecimalField(label='Макимална цена', min_value=0, required=False, decimal_places=2, max_digits=10, error_messages={'max_digits': 'Максималната дължина е 10 цифри!', 'decimal_places': 'Максималната дължина след десетичната запетая е 2 цифри!', 'min_value': 'Минималната цена е 0€!'})
    desc_price = forms.BooleanField(label='Подреди низходящо по цена', required=False, initial=False)
    per_page = forms.ChoiceField(choices=PerPageChoices.choices, label='Брой резултати на страница', required=False, initial=PerPageChoices.FIVE)