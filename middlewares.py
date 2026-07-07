from http.client import responses

from django.http import HttpResponseForbidden, HttpRequest


class IsBannedMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):

        user = request.user

        if request.user.is_authenticated and hasattr(request.user, 'bans'):
            if user.is_full_banned():
                return HttpResponseForbidden()
            elif user.is_chat_banned() and request.path.startswith('/chat/'):
                return HttpResponseForbidden()
            elif user.is_comments_banned() and request.path.startswith('/comments/'):
                return HttpResponseForbidden()
            elif user.is_offer_service_banned() and (request.path.startswith('/services/create/') or request.path.startswith('/services/update/') or request.path.startswith('/services/delete/')):
                return HttpResponseForbidden()

        response = self.get_response(request)

        return response


from allauth.account.models import EmailAddress
from django.shortcuts import redirect

class BlockUnverifiedEmailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:

            email_obj = EmailAddress.objects.filter(
                user=user,
            ).first()



            if email_obj and not email_obj.verified:

                if not request.path.startswith('/accounts/confirm-email/'):
                    return redirect("/accounts/confirm-email/")

        return self.get_response(request)