from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, DetailView
from django.views.generic.edit import FormMixin, UpdateView

from comments.forms import CreateCommentForm
from services.forms import CreateServiceForm, DeleteServiceForm, SearchSortAndFilterServicesForm, UpdateServiceForm
from services.models import Service


# Create your views here.
class CreateService(CreateView):
    model = Service
    form_class = CreateServiceForm
    template_name = 'services/forms/create_service_form.html'

    def get_success_url(self):
        return reverse('all_services')

class UpdateService(UpdateView):
    model = Service
    form_class = UpdateServiceForm
    slug_field = 'slug'
    slug_url_kwarg = 'service_slug'
    template_name = 'services/forms/update_service_form.html'

    def get_success_url(self):
        return reverse('service_details', kwargs={'service_slug': self.object.slug})


class DeleteService(DeleteView):
    model = Service
    template_name = 'services/forms/delete_service_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'service_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteServiceForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('all_services')
    
class AllServices(ListView):
    model = Service
    template_name = 'services/all_services.html'
    context_object_name = 'services'

    def get_paginate_by(self, queryset):
        per_page = int(self.request.GET.get('per_page', 5))

        if per_page < 5:
            return 5
        return  min(per_page, 100)

    def get_queryset(self):
        queryset = super().get_queryset().select_related('programmer', 'type').prefetch_related('technologies', 'comments')
        self.form = SearchSortAndFilterServicesForm(self.request.GET)

        if self.form.is_valid():
            query = self.form.cleaned_data['search_query'].strip()
            service_type = self.form.cleaned_data['type']
            technologies = self.form.cleaned_data['technologies']
            min_price = self.form.cleaned_data['min_price']
            max_price = self.form.cleaned_data['max_price']
            desc_price = self.form.cleaned_data['desc_price']


            if query:
                queryset = queryset.filter(title__icontains=query)

            if service_type:
                queryset = queryset.filter(type=service_type)

            if technologies:
                queryset = queryset.filter(technologies__in=technologies)

            if min_price is not None:
                queryset = queryset.filter(min_price__gte=min_price)

            if max_price is not None:
                queryset = queryset.filter(max_price__lte=max_price)

            if desc_price:
                return queryset.order_by('-min_price')

        return queryset.distinct().order_by('min_price')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context

class ServiceDetails(FormMixin, DetailView):
    model = Service
    template_name = 'services/service_details.html'
    context_object_name = 'service'
    slug_field = 'slug'
    slug_url_kwarg = 'service_slug'
    form_class = CreateCommentForm

    def get_queryset(self):
        return super().get_queryset().select_related('programmer', 'type').prefetch_related('technologies', 'comments')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.service = self.object
        comment.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('service_details', kwargs={'service_slug': self.object.slug})



