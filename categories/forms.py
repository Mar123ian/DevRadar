from django import forms

from categories.models import Type, Technology


class TypeForm(forms.ModelForm):
    model = Type
    fields = ['name', 'description', 'image']

    class Meta:
        labels = {
            'name': 'Име',
            'description': 'Описание',
            'image': 'Изображение',
        }

class CreateTypeForm(TypeForm):
    pass

class DeleteTypeForm(TypeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = True
            self.fields[field].required = False

class TechnologyForm(forms.ModelForm):
    model = Technology
    fields = ['name', 'description', 'image']

    class Meta:
        labels = {
            'name': 'Име',
            'description': 'Описание',
            'image': 'Изображение',
        }

class CreateTechnologyForm(TechnologyForm):
    pass

class DeleteTechnologyForm(TechnologyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = True
            self.fields[field].required = False


