from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.routers import DefaultRouter

from services_api.views import ServicesViewSet, ApiInfo

router = DefaultRouter()
router.register('services', ServicesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('info/', ApiInfo.as_view(), name='api_info'),


]