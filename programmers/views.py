from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, DetailView, UpdateView

from accounts.models import ProgrammerUser
from moderation.mixins import EditorOrSuperuserRequiredMixin
from moderation.views import BaseCreateReportView
from programmers.forms import CreateProgrammerForm, DeleteProgrammerForm, UpdateProgrammerForm
from programmers.models import Programmer, ProgrammerReport


# Create your views here.
# class CreateProgrammer(CreateView):
#     model = Programmer
#     form_class = CreateProgrammerForm
#     template_name = 'programmers/forms/create_programmer_form.html'
#
#     def get_success_url(self):
#         return reverse('all_programmers')

class UpdateProgrammer(LoginRequiredMixin, UpdateView):
    model = ProgrammerUser
    form_class = UpdateProgrammerForm
    slug_field = 'slug'
    slug_url_kwarg = 'programmer_slug'
    template_name = 'programmers/forms/update_programmer_form.html'


    def get_form_kwargs(self):
        # Вземаме стандартните kwargs (които съдържат instance, data и files)
        kwargs = super().get_form_kwargs()
        # Добавяме request към тях, за да се прихване в __init__ на формуляра
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse('programmer_details', kwargs={'programmer_slug': self.object.slug})

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or request.user == self.get_object():
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def form_valid(self, form):
        user = self.get_object()
        new_email = form.cleaned_data['email']

        # --- handle email separately ---
        if new_email != user.email:
            UserModel = get_user_model()

            if UserModel.objects.filter(email=new_email).count() == 0:
                # 1. Изтриваме Google / Social връзките на потребителя
                SocialAccount.objects.filter(user=user, provider='google').delete()
                # Забележка: Ако искаш да изтриеш ВСИЧКИ социални входове (не само Google), ползвай:
                # SocialAccount.objects.filter(user=user).delete()

                # DO NOT update user.email here
                # mark existing email as non-primary (soft state)
                EmailAddress.objects.filter(user=user).update(primary=False)

                # create pending email
                email_obj, created = EmailAddress.objects.get_or_create(
                    user=user,
                    email=new_email,
                    defaults={
                        "verified": False,
                        "primary": False,
                    }
                )

                # send verification
                email_obj.send_confirmation(self.request)

                # IMPORTANT: prevent ModelForm from overwriting email immediately
                form.instance.email = user.email

        return super().form_valid(form)


class DeleteProgrammer(LoginRequiredMixin, DeleteView):
    model = ProgrammerUser
    template_name = 'programmers/forms/delete_programmer_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'programmer_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteProgrammerForm(instance=self.get_object())
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(
                name='Editors').exists() or request.user.is_superuser or request.user == self.get_object():
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()


    def get_success_url(self):
        return reverse('profile')

UserModel = get_user_model()
class AllProgrammers(ListView):
    model = ProgrammerUser
    template_name = 'programmers/all_programmers.html'
    context_object_name = 'programmers'
    paginate_by = 20  # Брой програмисти на страница

    def get_queryset(self):
        queryset = super().get_queryset()
        # Извикваме метода is_full_banned() с () за всеки обект
        return [p for p in queryset if (not p.is_full_banned() and not p.is_offer_service_banned())]

class ProgrammerDetails(LoginRequiredMixin, DetailView):
    model = ProgrammerUser
    template_name = 'programmers/programmer_details.html'
    context_object_name = 'programmer'
    slug_field = 'slug'
    slug_url_kwarg = 'programmer_slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('services')

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_full_banned():
            return HttpResponseNotFound()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Взимаме услугите (ако active_services е метод, извикайте го с active_services())
        services_list = self.object.active_services()


        # 2. Настройваме Paginator (напр. по 6 услуги на страница)
        paginator = Paginator(services_list, 20)

        # 3. Взимаме номера на страницата от URL параметъра (?page=1)
        page_number = self.request.GET.get("page")
        services = paginator.get_page(page_number)

        context["services"] = services
        return context


class CreateProgrammerReport(BaseCreateReportView):
    template_name = 'programmers/forms/create_programmer_report.html'
    model_to_report = ProgrammerUser
    object_target_field = 'programmer'
    report_model = ProgrammerReport

    def get_success_url(self):
        return reverse('programmer_details', kwargs={'programmer_slug': self.target_object.slug})

from django.views.generic import ListView

class ProgrammerReportListView(EditorOrSuperuserRequiredMixin, ListView):
    model = ProgrammerReport
    template_name = 'programmers/programmer_report_list.html'
    context_object_name = 'reports'
    ordering = ['-timestamp']
    paginate_by = 20
