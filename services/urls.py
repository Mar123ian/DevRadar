from django.urls import path

from services.views import CreateService, DeleteService, AllServices, ServiceDetails, UpdateService, FavouriteServices, \
    CreateServiceReport, ServiceReportListView, DeleteServiceDueToViolation, RestoreServiceFromViolation

urlpatterns = [

path("delete_service_due_to_violation/<int:pk>/", DeleteServiceDueToViolation.as_view(), name='delete_service_due_to_violation'),
    path("restore_service_from_violation/<int:pk>/", RestoreServiceFromViolation.as_view(),
         name='restore_service_from_violation'),
    path("all_reported_services/", ServiceReportListView.as_view(), name='all_reported_services'),

    path('all/', AllServices.as_view(), name='all_services'),
    path('favourites/', FavouriteServices.as_view(), name='favourite_services'),
    path('create/', CreateService.as_view(), name='create_service'),
    path('delete/<slug:service_slug>/', DeleteService.as_view(), name='delete_service'),
    path('update/<slug:service_slug>/', UpdateService.as_view(), name='update_service'),
    path('<slug:service_slug>/', ServiceDetails.as_view(), name='service_details'),
path("report_service/<int:pk>/", CreateServiceReport.as_view(), name='report_service'),

]