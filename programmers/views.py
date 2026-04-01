from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, DetailView, UpdateView

from accounts.models import ProgrammerUser
from programmers.forms import CreateProgrammerForm, DeleteProgrammerForm, UpdateProgrammerForm
from programmers.models import Programmer


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

    def get_success_url(self):
        return reverse('programmer_details', kwargs={'programmer_slug': self.object.slug})

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or request.user == self.get_object():
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()


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



class ProgrammerDetails(LoginRequiredMixin, DetailView):
    model = ProgrammerUser
    template_name = 'programmers/programmer_details.html'
    context_object_name = 'programmer'
    slug_field = 'slug'
    slug_url_kwarg = 'programmer_slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('services')
