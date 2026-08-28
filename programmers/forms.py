import io

from PIL import Image
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from accounts.models import ProgrammerUser
from core.mixins import DisableFieldsMixin
from programmers.models import Programmer


class ProgrammerForm(forms.ModelForm):


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

    def clean_image(self):
        image = self.cleaned_data.get('image')  # Замени 'image' с името на твоето поле

        if image and hasattr(image, 'size'):
            # 10 MB в байтове (лимитът на Cloudinary)
            max_size = 10 * 1024 * 1024

            if image.size > max_size:
                raise ValidationError("Файлът е прекалено голям. Максималният позволен размер е 10 MB.")

        return image



class CreateProgrammerForm(ProgrammerForm):
    pass

class UpdateProgrammerForm(ProgrammerForm):

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

class DeleteProgrammerForm(DisableFieldsMixin, ProgrammerForm):
    pass