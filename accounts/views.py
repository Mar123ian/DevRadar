from http.client import responses

from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.http import HttpResponseForbidden, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView, TemplateView, FormView

from accounts.forms import ProgrammerCreationForm, DevRadarUserCreationForm, DevRadarUserUpdateForm, \
    DevRadarUserDeleteForm, UpgradeToProgrammerForm
from accounts.models import ProgrammerUser, DevRadarUser
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

    def get_form_kwargs(self):
        # Вземаме стандартните kwargs (които съдържат instance, data и files)
        kwargs = super().get_form_kwargs()
        # Добавяме request към тях, за да се прихване в __init__ на формуляра
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = self.get_object()
        new_email = form.cleaned_data['email']

        # --- handle email separately ---
        if new_email != user.email:
            UserModel = get_user_model()

            if UserModel.objects.filter(email=new_email).count() == 0:
                # 1. Изтриваме Google / Social връзките на потребителя
                SocialAccount.objects.filter(user=user, provider='google').delete()
                # Забележка: Ако искаш да изтриеш ВСИЧКИ социални входове (не само Google), ползвай:
                # SocialAccount.objects.filter(user=user).delete()

                # DO NOT update user.email here
                # mark existing email as non-primary (soft state)
                EmailAddress.objects.filter(user=user).update(primary=False)

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


from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.shortcuts import redirect, render
from django.utils.text import slugify
from unidecode import unidecode


@login_required
def upgrade_to_programmer(request):
    user = request.user

    # 1. Проверяваме дали вече не е програмист
    if user.is_programmer:
        messages.info(request, "Вие вече сте регистриран като програмист!")
        return redirect('home')

    if request.method == 'POST':
        form = UpgradeToProgrammerForm(request.POST, request.FILES)

        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            uploaded_image = form.cleaned_data.get('image')

            # 2. Генерираме slug за програмиста
            full_name = user.get_full_name() or user.username
            base_slug = slugify(unidecode(full_name))
            count = ProgrammerUser.objects.filter(slug=base_slug).count()
            slug = f"{base_slug}{count + 1}" if count > 0 else base_slug

            with transaction.atomic():
                # А) Записваме изображението през Storage API на Django (ако има такова)
                image_path = ''
                if uploaded_image:
                    temp_programmer = ProgrammerUser(image=uploaded_image)
                    temp_programmer.image.save(uploaded_image.name, uploaded_image, save=False)
                    image_path = temp_programmer.image.name

                # Б) Обновяваме polymorphic_ctype в родителската таблица без да променяме другите полета
                programmer_ct = ContentType.objects.get_for_model(ProgrammerUser)
                DevRadarUser.objects.filter(pk=user.pk).update(polymorphic_ctype=programmer_ct)

                # В) Вмъкваме запис ДИРЕКТНО в таблицата на ProgrammerUser
                child_table = ProgrammerUser._meta.db_table
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"""
                        INSERT INTO {child_table} (devradaruser_ptr_id, phone_number, image, slug)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [user.pk, phone_number, image_path, slug]
                    )

                # Г) Добавяме към групата "Programmers"
                group, _ = Group.objects.get_or_create(name="Programmers")
                user.groups.add(group)

            # 3. Вземаме обновения обект от базата данни (Django го зарежда като ProgrammerUser)
            programmer = ProgrammerUser.objects.get(pk=user.pk)

            # 4. Презареждаме сесията
            login(request, programmer, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, "Успешно надградихте профила си!")
            return redirect('home')
    else:
        form = UpgradeToProgrammerForm()

    return render(request, 'accounts/upgrade_to_programmer.html', {'form': form})


from django.contrib import messages
from django.shortcuts import redirect
from django.views import View

from allauth.account.models import EmailAddress


from django.contrib import messages
from django.shortcuts import redirect
from django.views import View

from allauth.account.models import EmailAddress


class ResendEmailView(View):


    def post(self, request, *args, **kwargs):

        email_address = None
        print(11)
        # 1. Ако има логнат потребител - търсим негов непотвърден email
        if request.user.is_authenticated:
            print(1)
            email_address = (
                EmailAddress.objects
                .filter(
                    user=request.user,
                    verified=False,
                    primary=True,
                ).first()
            )

        # 2. Ако няма - използваме session-а от регистрацията
        if not email_address:
            print(2)
            email = request.session.get(
                "pending_verification_email"
            )

            if email:
                email_address = (
                    EmailAddress.objects
                    .filter(
                        email=email,
                        verified=False
                    )
                    .first()
                )

                print(email_address)
                print(email)
        # TODO проверка какво прави
        if not email_address:
            messages.error(
                request,
                "No pending email verification found."
            )
            return redirect("account_signup")

        # изпращане на confirmation email
        email_address.send_confirmation(request)

        messages.success(
            request,
            "A new confirmation email has been sent."
        )

        return redirect(
            "account_email_verification_sent"
        )

    def dispatch(self, request, *args, **kwargs):
        print(f"Заявка метод: {request.method} | Потребител логнат: {request.user.is_authenticated}")
        return super().dispatch(request, *args, **kwargs)

class RestoreOldEmail(View):

    def post(self, request: HttpRequest, *args, **kwargs):
        EmailAddress.objects.filter(user=request.user, verified=False).delete()
        email = EmailAddress.objects.filter(user=request.user, verified=True).first()
        email.primary = True
        email.save()
        email_in_text = email.email
        request.user.email = email_in_text

        if request.user.is_programmer:
            return redirect("update_programmer", programmer_slug = request.user.slug)

        else:
            return redirect("update_user", pk=request.user.id)

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        primary_emails = EmailAddress.objects.filter(user=request.user, primary=True)
        if not (request.user.is_authenticated and not primary_emails):
            return HttpResponseForbidden()

        else:
            return super().dispatch(request, *args, **kwargs)