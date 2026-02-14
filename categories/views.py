from django.shortcuts import render
from django.views.generic import CreateView, DeleteView

from categories.forms import CreateTypeForm, DeleteTypeForm, CreateTechnologyForm, DeleteTechnologyForm
from categories.models import Type, Technology


# Create your views here.
class CreateType(CreateView):
    model = Type
    form_class = CreateTypeForm
    template_name = 'categories/forms/create_type_form.html'

class DeleteType(DeleteView):
    model = Type
    template_name = 'categories/forms/delete_type_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteTypeForm(instance=self.get_object())
        return context

class CreateTechnology(CreateView):
    model = Technology
    form_class = CreateTechnologyForm
    template_name = 'categories/forms/create_technology_form.html'

class DeleteTechnology(DeleteView):
    model = Technology
    template_name = 'categories/forms/delete_technology_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteTechnologyForm(instance=self.get_object())
        return context
