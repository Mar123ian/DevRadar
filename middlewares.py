from http.client import responses

from django.http import HttpResponseForbidden, HttpRequest


class IsBannedMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):

        user = request.user

        if request.user.is_authenticated and hasattr(request.user, 'bans'):
            if user.is_full_banned() and not request.path.startswith('/moderation/violations/') and not request.path.startswith('/moderation/appeal'):
                return render(request, 'moderation/banned_full.html', status=403)
            elif user.is_chat_banned() and request.path.startswith('/chat/') and not request.path.startswith('/chat/appeal_message_violation'):
                return render(request, 'moderation/banned_chat.html', status=403)
            elif user.is_comments_banned() and request.path.startswith('/comments/'):
                return render(request, 'moderation/banned_comments.html', status=403)
            elif user.is_offer_service_banned() and (request.path.startswith('/services/create/') or request.path.startswith('/services/update/') or request.path.startswith('/services/delete/')):
                return render(request, 'moderation/banned_services.html', status=403)

        response = self.get_response(request)

        return response


from allauth.account.models import EmailAddress
from django.shortcuts import redirect, render

class BlockUnverifiedEmailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            # TODO какво ако са много имейли
            email_obj = EmailAddress.objects.filter(
                user=user,
            ).last()



            if email_obj and not email_obj.verified:

                if not (request.path.startswith('/accounts/confirm-email/') or request.path.startswith('/accounts/resend-confirmation-email/') or request.path.startswith('/accounts/restore_old_email/')):
                    return redirect("/accounts/confirm-email/")

        return self.get_response(request)


# myapp/middleware.py
from django.utils import translation

class ForceDefaultLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ако няма записана бисквитка за език, форсираме 'bg'
        if 'django_language' not in request.COOKIES:
            translation.activate('bg')
            request.LANGUAGE_CODE = 'bg'
        return self.get_response(request)