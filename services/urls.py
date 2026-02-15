from django.urls import path

from services.views import CreateService, DeleteService

urlpatterns = [
    path('create/', CreateService.as_view(), name='create_service'),
    path('delete/<slug:service_slug>/', DeleteService.as_view(), name='delete_service'),

]