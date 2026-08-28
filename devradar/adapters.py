import uuid

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        # Първо извиква вграденото попълване
        user = super().populate_user(request, sociallogin, data)

        # Ако има имейл, генерира уникално потребителско име
        if user.email:
            base_username = user.email.split('@')[0]
            User = get_user_model()

            while True:
                # Генерираме потенциално потребителско име
                new_username = f"{base_username}_{uuid.uuid4().hex[:6]}"

                # Проверяваме дали вече съществува в базата данни
                if not User.objects.filter(username=new_username).exists():
                    user.username = new_username
                    break  # Намерено е уникално име, излизаме от цикъла

        return user

    def pre_social_login(self, request, sociallogin):
        # 1. Ако социалният акаунт вече е свързан с потребител, не правим нищо
        if sociallogin.is_existing:
            return

        # 2. Вземаме имейла от Google профила
        email = sociallogin.user.email
        if not email:
            return

        User = get_user_model()

        try:
            # 3. Проверяваме дали съществува локален потребител с този имейл
            existing_user = User.objects.get(email=email)

            # 4. Проверяваме дали този потребител вече няма свързан Google акаунт
            # (за да не презапишем чужд социален профил)
            if not SocialAccount.objects.filter(user=existing_user, provider=sociallogin.account.provider).exists():

                # 5. Свързваме социалния профил с намерени локален потребител
                sociallogin.connect(request, existing_user)

                # 6. (Бонус) Маркираме имейла като верифициран, за да не му досаждаме
                email_address, created = EmailAddress.objects.get_or_create(
                    user=existing_user,
                    email=email,
                    defaults={'verified': True, 'primary': True}
                )
                if not email_address.verified:
                    email_address.verified = True
                    email_address.save()

        except User.DoesNotExist:
            # Ако потребителят не съществува, Allauth ще си продължи по стандартния път за регистрация
            pass


from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):

    def get_password_change_redirect_url(self, request):
        #TODO да казва че е успешно, анимация докато зарежда
        return reverse('profile')

    def pre_login(self, request, user, **kwargs):
        print('In pre_login')
        if user and user.email:
            print("user.email")
            # 1. Записваме имейла
            request.session['pending_verification_email'] = user.email

            # 2. ЗАДЪЛЖИТЕЛНО: Казваме на Django да запази сесията за AnonymousUser
            request.session.modified = True

        return super().pre_login(request, user, **kwargs)


    def clean_email(self, email):
        email = super().clean_email(email)
        print(f"--- [DEBUG] Започва проверка за имейл: {email} ---")

        if email:
            email_lower = email.lower().strip()
            unverified_emails = EmailAddress.objects.filter(email__iexact=email_lower, verified=False)

            print(f"[DEBUG] Намерени непотвърдени записи: {unverified_emails.count()}")

            for unverified_email in unverified_emails:
                user = unverified_email.user
                print(f"[DEBUG] Проверка на потребител: {user.username} (ID: {user.id})")

                other_emails = EmailAddress.objects.filter(user=user).exclude(id=unverified_email.id)

                if other_emails.exists():
                    print(f"[DEBUG] Потребителят {user.username} има други имейли. Връщаме стария.")
                    old_email_address = other_emails.order_by('id').first()
                    unverified_email.delete()

                    old_email_address.primary = True
                    old_email_address.save()

                    user.email = old_email_address.email
                    user.save()
                else:
                    print(f"[DEBUG] Потребителят {user.username} няма други имейли. ИЗТРИВАМЕ целия профил.")
                    # Ако имаш модели, свързани с User чрез models.PROTECT, това изтриване ще гръмне.
                    user.delete()
                    print("[DEBUG] Успешно изтриване!")

        return email