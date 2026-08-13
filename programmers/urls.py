from django.urls import path

from programmers.views import DeleteProgrammer, AllProgrammers, ProgrammerDetails, UpdateProgrammer, \
    CreateProgrammerReport, ProgrammerReportListView

urlpatterns = [
path("report_programmer/<int:pk>/", CreateProgrammerReport.as_view(), name='report_programmer'),
    path("all_reported_programmers/", ProgrammerReportListView.as_view(), name='all_reported_programmers'),
    path('all/', AllProgrammers.as_view(), name='all_programmers'),
    path('update/<slug:programmer_slug>/', UpdateProgrammer.as_view(), name='update_programmer'),
    path('delete/<slug:programmer_slug>/', DeleteProgrammer.as_view(), name='delete_programmer'),
    path('<slug:programmer_slug>/', ProgrammerDetails.as_view(), name='programmer_details'),

]