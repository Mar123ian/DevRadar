

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

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

class ApiInfo(LoginRequiredMixin, TemplateView):
    template_name = 'services_api/api_info.html'

    def post(self, request, *args, **kwargs):
        user = request.user

        token, created = Token.objects.get_or_create(user=user)

        if not created:
            token.delete()
            token, created = Token.objects.get_or_create(user=user)
        return render(request, self.template_name, {'token': token})

    def get_context_data(self, **kwargs):
        try:
            token = Token.objects.get(user=self.request.user)
        except Token.DoesNotExist:
            token = None

        kwargs['token'] = token

        return kwargs

