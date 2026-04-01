from http.client import responses

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView, TemplateView

from accounts.forms import ProgrammerCreationForm, DevRadarUserCreationForm, DevRadarUserUpdateForm, \
    DevRadarUserDeleteForm


# Create your views here.
class RegisterProgrammerUserView(CreateView):
    form_class = ProgrammerCreationForm
    template_name = 'accounts/register_programmer.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.object

        group, created = Group.objects.get_or_create(name="Programmers")
        user.groups.add(group)

        return response


class RegisterDevRadarUserView(CreateView):
    form_class = DevRadarUserCreationForm
    template_name = 'accounts/register_user.html'
    success_url = reverse_lazy('login')


class UpdateDevRadarUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = DevRadarUserUpdateForm
    template_name = 'accounts/forms/update_user_form.html'

    def get_success_url(self):
        return reverse('profile')

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(
                name='Editors').exists() or request.user.is_superuser or request.user == self.get_object():
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

class DeleteDevRadarUser(LoginRequiredMixin, DeleteView):
    model = get_user_model()
    template_name = 'accounts/forms/delete_user_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DevRadarUserDeleteForm(instance=self.get_object())
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(
                name='Editors').exists() or request.user.is_superuser or request.user == self.get_object():
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def get_success_url(self):
        return reverse('login')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

