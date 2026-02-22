from django.urls import path
from django.views.generic import RedirectView

from core.views import home

urlpatterns = [
    path('' ,home ,name='home'),
    path('home/', RedirectView.as_view(pattern_name='home'), name='redirect_home'),

]