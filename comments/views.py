from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views.generic import UpdateView, DeleteView

from comments.forms import UpdateCommentForm, DeleteCommentForm
from comments.models import Comment, CommentReport
from moderation.mixins import EditorOrSuperuserRequiredMixin
from moderation.views import BaseCreateReportView, DeleteContentDueToViolationBase, RestoreContentFromViolationBase


class UpdateComment(LoginRequiredMixin, UpdateView):

    model = Comment
    form_class = UpdateCommentForm
    template_name = 'comments/forms/update_comment_form.html'

    def get_success_url(self):
        return reverse('service_details', kwargs={'service_slug': self.get_object().service.slug})

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if (request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or
                (request.user == self.get_object().author and not (self.object.is_deleted_due_to_violation or self.object.is_deleted_due_to_ban))):
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
        self.object = self.get_object()

        if (request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or
                (request.user == self.get_object().author and not (self.object.is_deleted_due_to_violation or self.object.is_deleted_due_to_ban))):
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

from django.urls import reverse
from django.shortcuts import get_object_or_404

class CreateCommentReport(BaseCreateReportView):
    template_name = 'comments/forms/create_comment_report.html'
    model_to_report = Comment
    object_target_field = 'comment'
    report_model = CommentReport

    def get_success_url(self):
        return reverse('service_details', kwargs={'service_slug': self.target_object.service.slug})

from django.views.generic import ListView
from .models import CommentReport

class CommentReportListView(EditorOrSuperuserRequiredMixin, ListView):
    model = CommentReport
    template_name = 'comments/comment_report_list.html'
    context_object_name = 'reports'
    ordering = ['-timestamp']


class DeleteCommentDueToViolation(DeleteContentDueToViolationBase):
    model = Comment

    def get_success_url(self):
        return reverse('all_reported_comments')


class RestoreCommentFromViolation(RestoreContentFromViolationBase):
    model = Comment

    def get_success_url(self):
        return reverse('all_reported_comments')