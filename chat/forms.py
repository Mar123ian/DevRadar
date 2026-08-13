from django import forms

from chat.models import Message
from comments.models import Comment
from core.mixins import DisableFieldsMixin


class MessageForm(forms.ModelForm):


    class Meta:
        model = Message

        fields = ['text', "file"]



class CreateMessageForm(MessageForm):
    pass

class UpdateMessageForm(MessageForm):
    pass

class DeleteMessageForm(DisableFieldsMixin, MessageForm):
    pass

