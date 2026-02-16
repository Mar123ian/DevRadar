from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, ListView, DetailView

from programmers.forms import CreateProgrammerForm, DeleteProgrammerForm
from programmers.models import Programmer


# Create your views here.
class CreateProgrammer(CreateView):
    model = Programmer
    form_class = CreateProgrammerForm
    template_name = 'programmers/forms/create_programmer_form.html'

class DeleteProgrammer(DeleteView):
    model = Programmer
    template_name = 'programmers/forms/delete_programmer_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'programmer_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteProgrammerForm(instance=self.get_object())
        return context
    
class AllProgrammers(ListView):
    model = Programmer
    template_name = 'programmers/all_programmers.html'
    context_object_name = 'programmers'

class ProgrammerDetails(DetailView):
    model = Programmer
    template_name = 'programmers/programmer_details.html'
    context_object_name = 'programmer'
    slug_field = 'slug'
    slug_url_kwarg = 'programmer_slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('services')