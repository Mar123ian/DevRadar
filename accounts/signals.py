from allauth.account.models import EmailAddress
from django.dispatch import receiver
from allauth.account.signals import email_confirmed, user_logged_in


@receiver(email_confirmed)
def email_confirmed_sync(sender, request, email_address, **kwargs):
    user = email_address.user

    # 1) set as primary
    EmailAddress.objects.filter(user=user).update(primary=False)
    email_address.primary = True
    email_address.verified = True
    email_address.save()

    EmailAddress.objects.filter(user=user, primary=False).exclude(pk=email_address.pk).delete()

    print('Email confirmed!')

    # 2) sync to User model
    user.email = email_address.email
    user.save()

@receiver(user_logged_in)
def set_email_in_session(sender, request, user, **kwargs):
    print('User logged in!')
    # Записваме имейла на влезелия потребител в сесията
    if user and user.email:
        print('Email in session:', user.email)
        request.session['pending_verification_email'] = user.email