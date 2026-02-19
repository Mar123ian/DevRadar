from django.urls import path

from programmers.views import CreateProgrammer, DeleteProgrammer, AllProgrammers, ProgrammerDetails, UpdateProgrammer

urlpatterns = [
    path('all/', AllProgrammers.as_view(), name='all_programmers'),
    path('create/', CreateProgrammer.as_view(), name='create_programmer'),
    path('update/<slug:programmer_slug>/', UpdateProgrammer.as_view(), name='update_programmer'),
    path('delete/<slug:programmer_slug>/', DeleteProgrammer.as_view(), name='delete_programmer'),
    path('<slug:programmer_slug>/', ProgrammerDetails.as_view(), name='programmer_details'),

]