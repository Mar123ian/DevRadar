from sqlite3 import IntegrityError

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, DetailView
from django.views.generic.edit import FormMixin, UpdateView

from accounts.models import ProgrammerUser
from chat.models import MessageReport
from comments.forms import CreateCommentForm
from moderation.mixins import EditorOrSuperuserRequiredMixin
from services.forms import CreateServiceForm, DeleteServiceForm, SearchSortAndFilterServicesForm, UpdateServiceForm
from services.models import Service, ServiceAppeal


# Create your views here.
class CreateService(LoginRequiredMixin, CreateView):
    model = Service
    form_class = CreateServiceForm
    template_name = 'services/forms/create_service_form.html'


    def get_success_url(self):
        return reverse('all_services')

    def form_valid(self, form):
        service = form.cleaned_data.get('name')
        programmer = self.request.user

        if programmer.services.all() and programmer.services.filter(name=service).exists():

            form.add_error('name',"Този програмист вече е предложил същата услуга!")
            return super().form_invalid(form)


        form.instance.programmer = programmer
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Programmers').exists():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

class UpdateService(LoginRequiredMixin, UpdateView):
    model = Service
    form_class = UpdateServiceForm
    slug_field = 'slug'
    slug_url_kwarg = 'service_slug'
    template_name = 'services/forms/update_service_form.html'

    def get_success_url(self):
        return reverse('service_details', kwargs={'service_slug': self.object.slug})

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if (request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or
                (request.user == self.get_object().programmer and not (
                        self.object.is_deleted_due_to_violation or self.object.is_deleted_due_to_ban))):
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

class DeleteService(LoginRequiredMixin, DeleteView):
    model = Service
    template_name = 'services/forms/delete_service_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'service_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteServiceForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('all_services')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if (request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or
                (request.user == self.get_object().programmer and not (self.object.is_deleted_due_to_violation or self.object.is_deleted_due_to_ban))):
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()
    
class AllServices(ListView):
    model = Service
    template_name = 'services/all_services.html'
    context_object_name = 'services'

    def get_paginate_by(self, queryset):
        per_page = int(self.request.GET.get('per_page', 5))

        if per_page < 5:
            return 5
        return  min(per_page, 100)

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_deleted_due_to_violation=False, is_deleted_due_to_ban=False).select_related('programmer', 'type').prefetch_related('technologies', 'comments')
        self.form = SearchSortAndFilterServicesForm(self.request.GET)

        if self.form.is_valid():
            query = self.form.cleaned_data['search_query'].strip()
            service_type = self.form.cleaned_data['type']
            technologies = self.form.cleaned_data['technologies']
            min_price = self.form.cleaned_data['min_price']
            max_price = self.form.cleaned_data['max_price']
            desc_price = self.form.cleaned_data['desc_price']


            if query:
                queryset = queryset.filter(name__icontains=query)

            if service_type:
                queryset = queryset.filter(type=service_type)

            if technologies:
                queryset = queryset.filter(technologies__in=technologies)

            if min_price is not None:
                queryset = queryset.filter(min_price__gte=min_price)

            if max_price is not None:
                queryset = queryset.filter(max_price__lte=max_price)

            if desc_price:
                return queryset.distinct().order_by('-min_price')

        return queryset.distinct().order_by('min_price')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context

class FavouriteServices(AllServices):
    template_name = 'services/favourite_services.html'

    def get_queryset(self):
        return super().get_queryset().filter(users=self.request.user)

class ServiceDetails(LoginRequiredMixin, FormMixin, DetailView):
    model = Service
    template_name = 'services/service_details.html'
    context_object_name = 'service'
    slug_field = 'slug'
    slug_url_kwarg = 'service_slug'
    form_class = CreateCommentForm

    #TODO Важна опционална препоръка за DB Optimization Ако service.active_comments е property във вашия модел Service (например return self.comments.filter(...)), е добре да се уверите, че връща QuerySet (без да извиква .all() вътре в имота), за да може Django Paginator да направи оптимизирана заявка COUNT(*) вместо да зарежда целия списък в паметта.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Взимаме коментарите от услугата
        comments_list = self.object.active_comments()

        # 2. Пагинатор - задайте броя коментари на страница (напр. 5)
        paginator = Paginator(comments_list, 20)

        # 3. Взимаме текущата страница от URL-а (?page=1)
        page_number = self.request.GET.get('page')
        comments = paginator.get_page(page_number)

        context['comments'] = comments
        return context

    def get_queryset(self):

        if self.request.user.groups.filter(name='Editors').exists() or self.request.user.is_superuser:
            return (
                super().get_queryset()
                .select_related('programmer', 'type')
                .prefetch_related('technologies', 'comments')
            )

        return (
            super().get_queryset()
            .filter(is_deleted_due_to_violation=False,
                    is_deleted_due_to_ban=False)  # Automatically returns 404 if soft-deleted
            .select_related('programmer', 'type')
            .prefetch_related('technologies', 'comments')
        )

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', None)
        self.object = self.get_object()

        if action == 'add_to_favourites':
            return self.add_to_favourites(request)

        if action == 'remove_from_favourites':
            return self.remove_from_favourites(request)


        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def add_to_favourites(self, request):
        request.user.favourites.add(self.object)
        return redirect(self.get_success_url())

    def remove_from_favourites(self, request):
        request.user.favourites.remove(self.object)
        return redirect(self.get_success_url())

    def form_valid(self, form):

        if self.request.user.is_comments_banned():
            return render(self.request, 'moderation/banned_comments.html', status=403)

        comment = form.save(commit=False)
        comment.service = self.object
        comment.author = self.request.user
        comment.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('service_details', kwargs={'service_slug': self.object.slug})





from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import get_object_or_404

from django.urls import reverse
from moderation.views import BaseCreateReportView, DeleteContentDueToViolationBase, RestoreContentFromViolationBase, \
    BaseCreateAppealView
from services.models import Service, ServiceReport

class CreateServiceReport(BaseCreateReportView):
    template_name = 'services/forms/create_service_report.html'
    model_to_report = Service
    object_target_field = 'service'
    report_model = ServiceReport

    def get_success_url(self):
        return reverse('service_details', kwargs={'service_slug': self.target_object.slug})

class CreateServiceAppeal(BaseCreateAppealView):
    template_name = 'services/forms/create_service_appeal.html'
    model_to_appeal = Service
    object_target_field = 'service'
    appeal_model = ServiceAppeal

    def get_success_url(self):
        return reverse('home')

from django.views.generic import ListView
from .models import ServiceReport

class ServiceReportListView(EditorOrSuperuserRequiredMixin, ListView):
    model = ServiceReport
    template_name = 'services/service_report_list.html'
    context_object_name = 'reports'
    ordering = ['-timestamp']
    paginate_by = 20

class DeleteServiceDueToViolation(DeleteContentDueToViolationBase):
    model = Service

    def get_success_url(self):
        return reverse('all_reported_services')


class RestoreServiceFromViolation(RestoreContentFromViolationBase):
    model = Service

    def get_success_url(self):
        return reverse('all_reported_services')


