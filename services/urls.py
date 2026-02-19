from django.urls import path

from services.views import CreateService, DeleteService, AllServices, ServiceDetails, UpdateService

urlpatterns = [
    path('all/', AllServices.as_view(), name='all_services'),
    path('create/', CreateService.as_view(), name='create_service'),
    path('delete/<slug:service_slug>/', DeleteService.as_view(), name='delete_service'),
    path('update/<slug:service_slug>/', UpdateService.as_view(), name='update_service'),
    path('<slug:service_slug>/', ServiceDetails.as_view(), name='service_details'),

]