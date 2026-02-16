from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, DetailView
from django.views.generic.edit import FormMixin

from comments.forms import CreateCommentForm
from services.forms import CreateServiceForm, DeleteServiceForm
from services.models import Service


# Create your views here.
class CreateService(CreateView):
    model = Service
    form_class = CreateServiceForm
    template_name = 'services/forms/create_service_form.html'

class DeleteService(DeleteView):
    model = Service
    template_name = 'services/forms/delete_service_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'service_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteServiceForm(instance=self.get_object())
        return context
    
class AllServices(ListView):
    model = Service
    template_name = 'services/all_services.html'
    context_object_name = 'services'

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



