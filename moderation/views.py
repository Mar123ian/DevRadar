from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DeleteView, FormView, TemplateView, UpdateView

from accounts.models import ProgrammerUser
from moderation.forms import CreateBanForm, DeleteBanForm, UpdateBanForm, BaseReportForm, \
    DeleteContentDueToViolationForm, RestoreContentFromViolationForm
from moderation.models import Ban


class BanUser(FormView):
    form_class = CreateBanForm
    template_name = 'moderation/forms/ban_user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = get_user_model().objects.get(pk=self.kwargs['pk'])
        return context

    # TODO permissions not dispatch
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    #TODO optimize
    def form_valid(self, form):
        target_user = get_object_or_404(get_user_model(), pk=self.kwargs['pk'])
        form_data = form.cleaned_data
        ban_type = form_data['ban_type']

        if (target_user.is_chat_banned() and ban_type == 'CHAT_BAN' or
                target_user.is_comments_banned() and ban_type == 'COMMENTS_BAN' or
        target_user.is_full_banned() and ban_type == 'FULL_BAN' or
        target_user.is_offer_service_banned() and ban_type == 'OFFER_SERVICE_BAN'):
            form.add_error(None, "Потребителят вече има такъв бан. Изтрийте стария, преди да добавяте нов или редактирайте настоящия!")
            return super().form_invalid(form)

        ban_instance = form.save(commit=False)
        ban_instance.user = target_user
        ban_instance.save()

        if ban_type == 'COMMENTS_BAN' or ban_type == 'FULL_BAN':

            for comment in target_user.comments.all():
                comment.is_deleted_due_to_ban = True
                comment.save()

        if ban_type == 'CHAT_BAN' or ban_type == 'FULL_BAN':

            for message in target_user.messages.all():
                message.is_deleted_due_to_ban = True
                message.save()

        if ban_type == 'OFFER_SERVICE_BAN' or ban_type == 'FULL_BAN':


            if isinstance(target_user, ProgrammerUser):
                for service in target_user.services.all():
                    service.is_deleted_due_to_ban = True
                    service.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')

class UpdateBan(LoginRequiredMixin, UpdateView):

    model = Ban
    form_class = UpdateBanForm
    template_name = 'moderation/forms/update_ban_form.html'

    def get_success_url(self):
        return reverse('all_users')


class DeleteBan(LoginRequiredMixin, DeleteView):
    model = Ban
    template_name = 'moderation/forms/remove_ban.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteBanForm(instance=self.get_object())
        return context

    # TODO permissions not dispatch
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        target_user = self.get_object().user
        ban_type = self.get_object().ban_type
        ban = self.get_object()

        #TODO repeated, optimize
        if ban_type == 'COMMENTS_BAN' or ban_type == 'FULL_BAN':

            for comment in target_user.comments.model.objects.all():
                comment.is_deleted_due_to_ban = False
                comment.save()

        if ban_type == 'CHAT_BAN' or ban_type == 'FULL_BAN':

            for message in target_user.messages.all():
                message.is_deleted_due_to_ban = False
                message.save()

        if ban_type == 'OFFER_SERVICE_BAN' or ban_type == 'FULL_BAN':


            if isinstance(target_user, ProgrammerUser):
                for service in target_user.services.model.objects.all():
                    service.is_deleted_due_to_ban = False
                    service.save()

        # Деактивиране на бана вместо физическо изтриване
        ban.active = False
        ban.save()

        return HttpResponseRedirect(self.get_success_url())


class AllUsers(LoginRequiredMixin, TemplateView):
    template_name = 'moderation/all_users.html'

    # TODO permissions not dispatch
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        UserModel = get_user_model()
        users = UserModel.objects.all().order_by('id')

        def _is_active(ban: Ban) -> bool:
            if not ban:
                return False
            if ban.active and ban.permanent:
                return True
            if ban.active and ban.duration:
                return ban.start_date + ban.duration > timezone.now()
            return False

        for u in users:
            active_bans = []
            unactive_bans = []
            for ban in u.bans.all().order_by('-start_date'):
                if _is_active(ban):
                    active_bans.append(ban)
                else:
                    unactive_bans.append(ban)

            # Attach computed fields used by the template
            u.active_bans = active_bans
            u.unactive_bans = unactive_bans

            if active_bans:
                first = active_bans[0]
                u.active_ban_type = first.ban_type
                u.active_ban_reason = first.reason
            else:
                u.active_ban_type = None
                u.active_ban_reason = None

            u.programmer_slug = getattr(u, 'slug', None)

        context['users'] = users
        return context


from django.views.generic import FormView
from django.shortcuts import get_object_or_404


class BaseCreateReportView(FormView):
    model_to_report = None
    report_model = None
    object_target_field = ''

    def dispatch(self, request, *args, **kwargs):
        self.target_object = get_object_or_404(self.model_to_report, pk=kwargs['pk'])

        if not isinstance(self.target_object, ProgrammerUser):
            if self.target_object.is_deleted_due_to_violation or self.target_object.is_deleted_due_to_ban:
                return HttpResponseNotFound()
        else:
            if self.target_object.is_full_banned():
                return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        report = form.save(commit=False)
        report.sender = self.request.user

        setattr(report, self.object_target_field, self.target_object)

        report.save()
        return super().form_valid(form)

    def get_form_class(self):
        return modelform_factory(
            self.report_model,
            form=BaseReportForm
        )



class DeleteContentDueToViolationBase(LoginRequiredMixin, DeleteView):
    form_class = DeleteContentDueToViolationForm
    template_name = 'moderation/forms/delete_content_due_to_violation_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def form_valid(self, form):
        # Вземаме съобщението от базата
        self.object = self.get_object()

        # Попълваме данните за софт делийт
        self.object.is_deleted_due_to_violation = True
        self.object.last_violation_info = {
            'reason': form.cleaned_data['reason'],
            'deleted_by_user_id': self.request.user.id,
            'deleted_by_username': self.request.user.username,
            'deleted_at': timezone.now().isoformat(),
        }
        self.object.save()

        # НЕ извикваме super().form_valid(form), за да НЕ изтрие Django записа от базата
        return redirect(self.get_success_url())


class RestoreContentFromViolationBase(LoginRequiredMixin, UpdateView):
    form_class = RestoreContentFromViolationForm
    template_name = 'moderation/forms/restore_content_from_violation_form.html'


    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance', None)  # Премахва instance аргумента
        return kwargs

    def form_valid(self, form):
        self.object = self.get_object()

        # Премахваме флага за изтриване
        self.object.is_deleted_due_to_violation = False

        # Запазваме историята в JSON полето
        info = self.object.last_violation_info or {}
        info['restored_by_user_id'] = self.request.user.id
        info['restored_by_username'] = self.request.user.username
        info['restored_at'] = timezone.now().isoformat()
        info['restoration_reason'] = form.cleaned_data.get('restoration_reason', '')

        self.object.last_violation_info = info
        self.object.save()

        return redirect(self.get_success_url())
