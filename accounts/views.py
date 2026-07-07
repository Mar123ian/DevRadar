from http.client import responses

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView, TemplateView, FormView

from accounts.forms import ProgrammerCreationForm, DevRadarUserCreationForm, DevRadarUserUpdateForm, \
    DevRadarUserDeleteForm, UpgradeToProgrammerForm
from accounts.models import ProgrammerUser
from django.contrib.auth import login

# Create your views here.
class RegisterProgrammerUserView(CreateView):
    form_class = ProgrammerCreationForm
    template_name = 'accounts/register_programmer.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.object

        group, created = Group.objects.get_or_create(name="Programmers")
        user.groups.add(group)

        return response


class RegisterDevRadarUserView(CreateView):
    form_class = DevRadarUserCreationForm
    template_name = 'accounts/register_user.html'
    success_url = reverse_lazy('login')


class UpdateDevRadarUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = DevRadarUserUpdateForm
    template_name = 'accounts/forms/update_user_form.html'

    def get_success_url(self):
        return reverse('profile')

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(
                name='Editors').exists() or request.user.is_superuser or request.user == self.get_object():
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def form_valid(self, form):
        user = self.get_object()
        new_email = form.cleaned_data['email']

        # --- handle email separately ---
        if new_email != user.email:
            UserModel = get_user_model()

            if UserModel.objects.filter(email=new_email).count() == 0:
                # DO NOT update user.email here
                # mark existing email as non-primary (soft state)
                EmailAddress.objects.filter(user=user).delete()

                # create pending email
                email_obj, created = EmailAddress.objects.get_or_create(
                    user=user,
                    email=new_email,
                    defaults={
                        "verified": False,
                        "primary": False,
                    }
                )

                # send verification
                email_obj.send_confirmation(self.request)

                # IMPORTANT: prevent ModelForm from overwriting email immediately
                form.instance.email = user.email

        return super().form_valid(form)

class DeleteDevRadarUser(LoginRequiredMixin, DeleteView):
    model = get_user_model()
    template_name = 'accounts/forms/delete_user_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DevRadarUserDeleteForm(instance=self.get_object())
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(
                name='Editors').exists() or request.user.is_superuser or request.user == self.get_object():
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def get_success_url(self):
        return reverse('login')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


@login_required
def upgrade_to_programmer(request):
    user = request.user

    # 1. Проверяваме дали вече не е програмист
    if user.is_programmer:
        messages.info(request, "Вие вече сте регистриран като програмист!")
        return redirect('home')  # Смени 'home' с името на началната ти страница

    if request.method == 'POST':
        form = UpgradeToProgrammerForm(request.POST, request.FILES)

        if form.is_valid():
            user = request.user

            # Използваме трансакция – ако нещо се провали, нищо няма да се изтрие
            with transaction.atomic():
                # 1. Запазваме оригиналната парола и всички базови данни
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'password': user.password,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'date_joined': user.date_joined,
                    'last_login': user.last_login,
                    # Добавете и вашите други специфични полета от DevRadarUser тук, ако има такива (напр. slug)
                }

                # 2. Изтриваме стария профил (това освобождава username и ID-то)
                user.delete()

                # 3. Създаваме изцяло новия програмист със същите базови данни + новите полета
                programmer = ProgrammerUser(
                    **user_data,
                    phone_number=form.cleaned_data['phone_number'],
                    image=form.cleaned_data.get('image')
                )



                # 4. Записваме обекта. Django ще създаде коректно редовете и в двете таблици.
                programmer.save()

                group, created = Group.objects.get_or_create(name="Programmers")
                programmer.groups.add(group)

            # 5. Тъй като изтрихме стария потребител, логваме новия обект обратно в сесията
            login(request, programmer, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, "Успешно надградихте профила си!")
            return redirect('home')
    else:
        form = UpgradeToProgrammerForm()

    return render(request, 'accounts/upgrade_to_programmer.html', {'form': form})

from django.contrib import messages
from django.shortcuts import redirect
from allauth.account.models import EmailAddress, EmailConfirmation


def resend_confirmation(request):
    if request.method == "POST":
        key = request.POST.get("key")

        try:
            confirmation = EmailConfirmation.objects.get(key=key)
            email_address = confirmation.email_address
            print(email_address)
            if not email_address.verified:
                email_address.send_confirmation(request)

        except EmailConfirmation.DoesNotExist:
            print(1)
            pass

        messages.info(request, "If possible, we resent the email.")

    return redirect(request.META.get("HTTP_REFERER", "/"))