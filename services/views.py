from django.shortcuts import render
from django.views.generic import CreateView, DeleteView

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