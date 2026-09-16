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

from django.dispatch import receiver
from allauth.account.signals import user_signed_up

@receiver(user_signed_up)
def track_meta_pixel_registration(request, user, **kwargs):
    if request:
        request.session['pixel_complete_registration'] = True
        # Изрично указваме на Django да запази промяната в сесията
        request.session.modified = True
        print("in user_signed_up")
        print(request.session.items())

