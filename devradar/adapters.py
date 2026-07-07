import uuid

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount


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

    def is_open_for_signup(self, request):
        email = request.POST.get('email')

        if email:
            email = email.lower().strip()

            # Намираме всички НЕпотвърдени записи за този имейл в системата
            unverified_emails = EmailAddress.objects.filter(email=email, verified=False)

            for unverified_email in unverified_emails:
                user = unverified_email.user

                # Проверяваме дали този потребител има И ДРУГИ имейли (т.е. сменил е имейла си)
                other_emails = EmailAddress.objects.filter(user=user).exclude(id=unverified_email.id)

                if other_emails.exists():
                    # СЛУЧАЙ 2: Потребителят е редактирал имейла си на чужд.
                    # Намираме най-новия потвърден или просто предишния му имейл по дата.
                    # Сортираме по дата на добавяне (или първичния ключ), за да вземем по-стария
                    old_email_address = other_emails.order_by('id').first()

                    # 1. Изтриваме само спорния нов непотвърден имейл адрес
                    unverified_email.delete()

                    # 2. Връщаме стария имейл като главен (primary)
                    old_email_address.primary = True
                    old_email_address.save()

                    # 3. Синхронизираме и основния модел на потребителя (User.email)
                    user.email = old_email_address.email
                    user.save()
                else:
                    # СЛУЧАЙ 1: Това е просто изоставен непотвърден профил (старата логика)
                    # Изтриваме целия потребител
                    user.delete()

        return super().is_open_for_signup(request)

