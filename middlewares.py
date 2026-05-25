from http.client import responses

from django.http import HttpResponseForbidden, HttpRequest


class IsBannedMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):

        user = request.user

        if request.user.is_authenticated and hasattr(request.user, 'bans'):
            if user.is_banned():
                return HttpResponseForbidden()
            elif user.is_chat_banned() and request.path.startswith('/chat/'):
                return HttpResponseForbidden()
            elif user.is_comments_banned() and request.path.startswith('/comments/'):
                return HttpResponseForbidden()
            elif user.is_offer_service_banned() and (request.path.startswith('/services/create/') or request.path.startswith('/services/update/') or request.path.startswith('/services/delete/')):
                return HttpResponseForbidden()

        response = self.get_response(request)

        return response