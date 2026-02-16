from django.shortcuts import render
from django.views.generic import CreateView, DeleteView

from comments.forms import CreateCommentForm
from comments.models import Comment


# Create your views here.
class CreateComment(CreateView):
    model = Comment
    form_class = CreateCommentForm
    template_name = 'comments/forms/create_comment_form.html'

