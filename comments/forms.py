from django import forms

from comments.models import Comment


class CommentForm(forms.ModelForm):


    class Meta:
        model = Comment

        fields = ['content']

        labels = {
            'content': 'Съдържание',
        }

        error_messages = {

            'content': {
                'required': 'Полето е задължително!'
            },
        }


class CreateCommentForm(CommentForm):
    pass