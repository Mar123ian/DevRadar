from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, DetailView

from categories.forms import CreateTypeForm, DeleteTypeForm, CreateTechnologyForm, DeleteTechnologyForm
from categories.models import Type, Technology


# Create your views here.
class CreateType(CreateView):
    model = Type
    form_class = CreateTypeForm
    template_name = 'categories/forms/create_type_form.html'

    def get_success_url(self):
        return reverse('all_types')

class DeleteType(DeleteView):
    model = Type
    template_name = 'categories/forms/delete_type_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'type_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteTypeForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('all_types')

class CreateTechnology(CreateView):
    model = Technology
    form_class = CreateTechnologyForm
    template_name = 'categories/forms/create_technology_form.html'

    def get_success_url(self):
        return reverse('home')

class DeleteTechnology(DeleteView):
    model = Technology
    template_name = 'categories/forms/delete_technology_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'technology_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteTechnologyForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('home')

class AllTypes(ListView):
    model = Type
    template_name = 'categories/all_types.html'
    context_object_name = 'types'

class TypeDetails(DetailView):
    model = Type
    template_name = 'categories/type_details.html'
    context_object_name = 'type'
    slug_field = 'slug'
    slug_url_kwarg = 'type_slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('services')

