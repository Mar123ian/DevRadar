from django.urls import path

from programmers.views import CreateProgrammer, DeleteProgrammer

urlpatterns = [
    path('create/', CreateProgrammer.as_view(), name='create_programmer'),
    path('delete/<slug:programmer_slug>/', DeleteProgrammer.as_view(), name='delete_programmer'),

]