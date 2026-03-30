from django.urls import path, include
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.routers import DefaultRouter

from services_api.views import ServicesViewSet

router = DefaultRouter()
router.register('services', ServicesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-token/', ObtainAuthToken.as_view(), name='get_token'),


]