from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import models

from django import forms

from accounts.models import DevRadarUser, ProgrammerUser
from core.mixins import DisableFieldsMixin

import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            raise ValidationError('Потребителското име не може да съдържа символа @.')
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isnumeric():
            raise ValidationError('Телефонният номер трябва да съдържа само цифри.')
        return phone_number

    def clean_image(self):  # Замени 'profile_image' с твоето име на поле
        image = self.cleaned_data.get('image')

        # Ако няма нова качена снимка или файлът е под 10 MB, не прави нищо
        if not image or not hasattr(image, 'size') or image.size <= 10 * 1024 * 1024:
            return image

        # Отваряме изображението
        img = Image.open(image)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Намаляваме резолюцията (напр. максимум 1920x1920 px)
        img.thumbnail((1920, 1920))

        # Компресираме го в паметта
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=80)
        output.seek(0)

        # Заменяме големия файл с новия компресиран файл
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image.name.split('.')[0]}.jpg",
            'image/jpeg',
            output.getbuffer().nbytes,
            None
        )

class ProgrammerCreationForm(ProgrammerBaseForm):
    pass


from django import forms
from allauth.account.forms import SignupForm


class DevRadarUserBaseForm(forms.ModelForm):
    class Meta:
        model = DevRadarUser
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
            'email': 'Въведете имейл', #TODO потр. име да е на български
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            raise ValidationError('Потребителското име не може да съдържа символа @.')
        return username


# Променяме наследяването, за да се свърже правилно с allauth
class DevRadarUserCreationForm(SignupForm, DevRadarUserBaseForm):

    def __init__(self, *args, **kwargs):
        # 1. Извикваме инициализацията на Allauth SignupForm, която добавя паролите и имейла по нейния си начин
        super().__init__(*args, **kwargs)

        # 2. Ръчно добавяме вашите полета от DevRadarUserBaseForm в allauth формуляра
        # Понеже allauth по подразбиране вече има username и email, добавяме първо и второ име
        self.fields['first_name'] = forms.CharField(
            max_length=150,
            required=True,  # Правим го задължително съгласно вашите изисквания за грешки
            label=self.Meta.labels['first_name'],
            help_text=self.Meta.help_texts['first_name'],
            error_messages=self.Meta.error_messages['first_name']
        )

        self.fields['last_name'] = forms.CharField(
            max_length=150,
            required=True,
            label=self.Meta.labels['last_name'],
            help_text=self.Meta.help_texts['last_name'],
            error_messages=self.Meta.error_messages['last_name']
        )

        # 3. Прилагаме вашите етикети и съобщения за грешки върху полетата, които allauth вече е създал
        self.fields['email'].label = self.Meta.labels['email']
        self.fields['email'].help_text = self.Meta.help_texts['email']
        self.fields['email'].error_messages.update(self.Meta.error_messages['email'])
        self.fields['email'].required = True

    def save(self, request):
        # Извикваме вградения save на allauth, който създава потребителя и паролата
        user = super().save(request)

        request.session["pending_verification_email"] = user.email
        print("cookie set with", request.COOKIES)

        # Записваме допълнителните полета от формуляра в потребителския модел
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        return user

class DevRadarUserUpdateForm(DevRadarUserBaseForm):

    def __init__(self, *args, **kwargs):
        # Вземаме request от подадените аргументи при създаване на формата
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        new_email = self.cleaned_data.get('email')

        # self.instance е текущият потребител
        if self.instance and self.instance.pk:
            # Проверяваме дали имейлът се променя
            if new_email != self.instance.email:
                # Проверяваме дали потребителят НЯМА парола (влязъл е само през Social Login)
                if not self.instance.has_usable_password():
                    raise forms.ValidationError(
                        "Трябва първо да създадете парола за профила си, тъй като промяната на имейла ще премахне входа с Google."
                    )

        return new_email

    def save(self, commit=True):
        # 1. Записваме обновената променлива `user` чрез стандартния ModelForm save
        user = super().save(commit=False)

        # 2. Обновяваме полетата от cleaned_data
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        print("in save")
        # 3. Достъпваме request през self.request, ако ни е необходим за сесията
        if self.request:
            print("in if")
            self.request.session["pending_verification_email"] = self.cleaned_data.get('email')

        # 4. Запазваме потребителя в базата данни
        if commit:
            user.save()

        return user
class DevRadarUserDeleteForm(DisableFieldsMixin, DevRadarUserBaseForm):
    pass

class UpgradeToProgrammerForm(forms.ModelForm):
    class Meta:
        model = ProgrammerUser
        fields = ['phone_number', 'image']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+359...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'phone_number': 'Телефонен номер',
            'image': 'Профилна снимка',
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isnumeric():
            raise ValidationError('Телефонният номер трябва да съдържа само цифри.')
        return phone_number


class ResendConfirmationForm(forms.Form):
    email = forms.EmailField()