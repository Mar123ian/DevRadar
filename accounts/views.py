from http.client import responses

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView

from accounts.forms import ProgrammerCreationForm, DevRadarUserCreationForm


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


