from django.shortcuts import render

from categories.models import Type


# Create your views here.
def home(request):
    service_types = Type.objects.all()
    return render(request, 'core/home.html', {'service_types': service_types})
