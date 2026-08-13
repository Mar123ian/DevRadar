from django.http import HttpRequest


def user_violations(request: HttpRequest):
    if request.user.is_authenticated:
        user = request.user
        chat_ban_duration, offer_service_ban_duration, comments_ban_duration = None, None, None
        chat_ban_reason, offer_service_ban_reason, comments_ban_reason = None, None, None


        is_chat_banned = user.is_chat_banned()
        if is_chat_banned:
            chat_ban = user.bans.filter(ban_type='CHAT_BAN', active=True).last()
            chat_ban_duration = chat_ban.duration if chat_ban.duration else None
            chat_ban_reason = chat_ban.reason

        is_offer_service_banned = request.user.is_offer_service_banned() if user.is_programmer else False
        if is_offer_service_banned:
            offer_service_ban = user.bans.filter(ban_type='OFFER_SERVICE_BAN', active=True).last()
            offer_service_ban_duration = offer_service_ban.duration if offer_service_ban.duration else None
            offer_service_ban_reason = offer_service_ban.reason


        is_comments_banned = user.is_comments_banned()
        if is_comments_banned:
            comments_ban = user.bans.filter(ban_type='COMMENTS_BAN', active=True).last()
            comments_ban_duration = comments_ban.duration if comments_ban.duration else None
            comments_ban_reason = comments_ban.reason


        messages = user.new_deleted_messages()
        comments = user.new_deleted_comments()
        services = user.new_deleted_services() if user.is_programmer else None
        print(services)

        return {'is_chat_banned': is_chat_banned,
                'chat_ban_duration': chat_ban_duration,
                'chat_ban_reason': chat_ban_reason,
                'is_offer_service_banned': is_offer_service_banned,
                'offer_service_ban_duration': offer_service_ban_duration,
                'offer_service_ban_reason': offer_service_ban_reason,
                'is_comments_banned': is_comments_banned,
                'comments_ban_duration': comments_ban_duration,
                'comments_ban_reason': comments_ban_reason,
                'messages': messages,
                'comments': comments,
                'services': services}
    return {}