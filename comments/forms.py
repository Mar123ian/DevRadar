from django import forms

from comments.models import Comment


class CommentForm(forms.ModelForm):


    class Meta:
        model = Comment

        fields = ['author', 'content']

        labels = {
            'author': 'Автор',
            'content': 'Съдържание',
        }

        error_messages = {
            'author': {
                'required': 'Полето е задължително!'
            },
            'content': {
                'required': 'Полето е задължително!'
            },
        }


class CreateCommentForm(CommentForm):
    pass