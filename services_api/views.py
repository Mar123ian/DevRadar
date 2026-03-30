from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication

from services.models import Service
from services_api.serializers import ServiceSerializer


# Create your views here.
class ServicesViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Service.objects.all().select_related('type', 'programmer').prefetch_related('technologies', 'comments__author')
