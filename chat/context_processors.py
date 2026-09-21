# chats/context_processors.py
from django.db.models import Subquery, OuterRef
from .models import Thread, Message

def unseen_threads_count(request):
    if request.user.is_authenticated:
        # Взимаме ID-то на изпращача (sender) от последното съобщение в съответната нишка
        latest_message_sender = Message.objects.filter(
            thread=OuterRef('pk')
        ).order_by('-timestamp').values('sender_id')[:1]

        # Филтрираме нишките:
        # 1. Потребителят участва в тях
        # 2. Не са изтрити (is_deleted=False)
        # 3. Маркирани са като невидяни (seen=False)
        # 4. Изключваме тези, чийто последен sender е текущият потребител
        count = Thread.objects.filter(
            users=request.user,
            is_deleted=False,
            seen=False
        ).annotate(
            last_sender_id=Subquery(latest_message_sender)
        ).exclude(
            last_sender_id=request.user.id
        ).count()

        return {'unseen_chats_count': count}

    return {'unseen_chats_count': 0}