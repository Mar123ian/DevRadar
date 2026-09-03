from http.client import responses

from django.http import HttpResponseForbidden, HttpRequest


class IsBannedMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):

        user = request.user

        if request.user.is_authenticated and hasattr(request.user, 'bans'):
            if user.is_full_banned() and not request.path.startswith('/moderation/violations/') and not request.path.startswith('/moderation/appeal') and not request.path.startswith('/programmers/delete') and not request.path.startswith('/accounts/delete'):
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

# middleware.py
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django_ratelimit.core import is_ratelimited

from django.http import HttpResponse  # или HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django_ratelimit.core import is_ratelimited


def get_real_client_ip(group, request):


    # 1. Cloudflare хедър
    cf_ip = request.META.get("HTTP_CF_CONNECTING_IP")
    if cf_ip:
        return f"ip:{cf_ip.strip()}"

    # 2. X-Forwarded-For (вземаме най-лявото IP - оригиналния клиент)
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        # Изчистваме празните пространства и вземаме първото IP
        ip = x_forwarded.split(",")[0].strip()
        return f"ip:{ip}"

    # 3. Директна връзка без прокси
    ip = request.META.get("REMOTE_ADDR")
    return f"ip:{ip}"


class GlobalRatelimitMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Игнорираме статични файлове и админ панел (по избор)
        if request.path.startswith(
            ("/static/", "/media/", "/admin/")
        ):
            return None

        was_limited = is_ratelimited(
            request=request,
            group="global_app_limit",
            key=get_real_client_ip,  # Нашата функция за реално IP
            rate="100/m",
            increment=True,
        )

        if was_limited:
            return redirect("/429/")


class RealIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Използваме вашата функция и премахваме "ip:" префикса за REMOTE_ADDR
        full_ip = get_real_client_ip(None, request)
        clean_ip = full_ip.replace("ip:", "")

        # Записваме истинското IP там, където Turnstile го търси
        request.META['REMOTE_ADDR'] = clean_ip

        return self.get_response(request)