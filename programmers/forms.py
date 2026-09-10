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

        fields = ['username', 'first_name', 'last_name', 'image', 'email', 'phone_number', 'site', 'bio']

        labels = {
            'first_name': 'Собствено име',
            'last_name': 'Фамилно име',
            'image': 'Изображение',
            'email': 'Имейл',
            'phone_number': 'Телефонен номер',
            'site': 'Сайт',
            'bio': 'Малко повече информация за вас',
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
            'first_name': 'Въведете собствено име или име на ИТ фирма',
            'last_name': 'Въведете фамилно име (ако сте фирма, може да го оставите празно)',
            'email': 'Въведете имейл',
            'phone_number': 'Телефонният номер НЕ Е ЗАДЪЛЖИТЕЛЕН, но може да е полезен за хората, които искат да се свържат с Вас. Ако го въведете, ще е видим за всички!',
            'image': 'Не е задължителна снимка. Ако сте фирма, можете да сложите вашето лого, ако сте човек, изображение на вас.',
            'site': 'Не е задължителен сайт. Ако разполагате с личен сайт, GitHub, Linktree с адреси или др. , сложете пълния му URL адрес в това поле, за да имат клиентите повече информация за вас и работата ви.',
            'bio': 'Също не е задължително. Свободен текст, например в коя сфера работите, образование, проекти и всичко полезно, за което се сетите :)',


        }

        widgets = {
            'site': forms.URLInput(attrs={'placeholder': 'https://...'})
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

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isnumeric():
            raise ValidationError('Телефонният номер трябва да съдържа само цифри.')
        return phone_number


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