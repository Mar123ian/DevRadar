from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views.generic import UpdateView, DeleteView

from comments.forms import UpdateCommentForm, DeleteCommentForm
from comments.models import Comment


class UpdateComment(LoginRequiredMixin, UpdateView):

    model = Comment
    form_class = UpdateCommentForm
    template_name = 'comments/forms/update_comment_form.html'

    def get_success_url(self):
        return reverse('service_details', kwargs={'service_slug': self.get_object().service.slug})

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or request.user == self.get_object().author:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

class DeleteComment(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'comments/forms/delete_comment_form.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteCommentForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('service_details', kwargs={'service_slug': self.get_object().service.slug})

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or request.user == self.get_object().author:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()