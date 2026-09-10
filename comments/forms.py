from django import forms

from comments.models import Comment
from core.mixins import DisableFieldsMixin


class CommentForm(forms.ModelForm):


    class Meta:
        model = Comment

        fields = ['content', 'rating']

        labels = {
            'content': 'Съдържание',
            'rating': 'Вашата оценка',
        }

        widgets = {
            'rating': forms.HiddenInput(),  # Скрива подразбиращия се input
        }

        error_messages = {

            'content': {
                'required': 'Полето е задължително!'
            },
            'rating': {
                'required': 'Полето е задължително!'
            },
        }


class CreateCommentForm(CommentForm):
    pass

class UpdateCommentForm(CommentForm):
    pass

class DeleteCommentForm(DisableFieldsMixin, CommentForm):
    pass