from django import forms

from comments.models import Comment


class CommentForm(forms.ModelForm):
    model = Comment
    fields = ['author', 'content']

    class Meta:
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