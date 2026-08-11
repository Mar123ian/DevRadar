from allauth.account.models import EmailAddress
from django.dispatch import receiver
from allauth.account.signals import email_confirmed

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