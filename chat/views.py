from celery.bin.celery import report
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models.aggregates import Max
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView

from moderation.mixins import EditorOrSuperuserRequiredMixin
from moderation.views import BaseCreateReportView, DeleteContentDueToViolationBase, RestoreContentFromViolationBase, \
    BaseCreateAppealView

from .forms import UpdateMessageForm
from .models import Thread, MessageReport, MessageAppeal
from .models import Message

User = get_user_model()

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    with transaction.atomic():
        thread = (
            Thread.objects
            .select_for_update()
            .filter(users=request.user)
            .filter(users=other_user)
            .first()
        )

        if not thread:
            thread = Thread.objects.create()
            thread.users.add(request.user, other_user)

    return redirect('chat_room', thread_id=thread.id)

from django.http import JsonResponse, HttpResponseForbidden

from django.core.files.storage import default_storage

import uuid
import os

from django.http import JsonResponse
from django.core.files.storage import default_storage


@login_required
def upload_file(request):

    ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf"]
    MAX_SIZE = 5 * 1024 * 1024

    if request.method == "POST" and request.FILES.get("file"):

        thread_id = request.POST.get("thread")
        thread = get_object_or_404(Thread, id=thread_id, users=request.user.id)

        file = request.FILES["file"]

        # взимаме extension-а (.jpg/.png/.pdf)
        ext = os.path.splitext(file.name)[1]

        # uuid filename
        filename = f"{uuid.uuid4()}{ext}"

        if ext.lower() not in ALLOWED_EXTENSIONS:
            return JsonResponse({"error": "invalid file"}, status=400)

        if file.size > MAX_SIZE:
            return JsonResponse({"error": "too large"}, status=400)

        # save
        path = default_storage.save(
            f"chat_files/{filename}",
            file
        )

        # media url
        url = default_storage.url(path)

        return JsonResponse({
            "url": url
        })

    return JsonResponse({
        "error": "no file"
    }, status=400)

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render


@login_required
def chat_room(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, users=request.user.id)

    # Взимаме последните 30 съобщения
    messages_qs = (
        Message.objects.filter(thread=thread)
        .select_related('sender')
        .order_by('-timestamp')[:30]
    )

    # Обръщаме ги в хронологичен ред (от по-стари към по-нови)
    messages = list(reversed(messages_qs))

    return render(
        request,
        'chat_room.html',
        {
            'thread': thread,
            'messages': messages,
            'has_more': Message.objects.filter(thread=thread).count() > 30,
        },
    )


# Допълнителен endpoint за зареждане на по-стари съобщения чрез AJAX
@login_required
def load_older_messages(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, users=request.user.id)
    last_message_id = request.GET.get('before_id')

    if not last_message_id:
        return JsonResponse({'messages': [], 'has_more': False})

    last_msg = get_object_or_404(Message, id=last_message_id, thread=thread)

    older_qs = (
        Message.objects.filter(thread=thread, timestamp__lt=last_msg.timestamp)
        .select_related('sender')
        .order_by('-timestamp')[:30]
    )

    has_more = older_qs.count() == 30
    messages_list = list(reversed(older_qs))

    data = []
    for msg in messages_list:
        is_deleted = (
            msg.is_deleted_due_to_violation or msg.is_deleted_due_to_ban
        )

        # ✅ Безопасно извличане на URL/път на файла като текст
        file_url = None
        if msg.file and not is_deleted:
            if hasattr(msg.file, 'url'):
                file_url = msg.file.url
            else:
                file_url = str(msg.file)

        data.append({
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.get_full_name() or msg.sender.username,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'text': msg.text if not is_deleted else None,
            'file': file_url,
            'is_deleted': is_deleted,
        })

    return JsonResponse({'messages': data, 'has_more': has_more})

from django.views.generic.edit import FormView, BaseDeleteView
from django.urls import reverse
from django.shortcuts import get_object_or_404

from django.http import JsonResponse

from django.http import JsonResponse

class CreateMessageReport(BaseCreateReportView):
    template_name = 'chat/forms/create_message_report.html'
    model_to_report = Message
    object_target_field = 'message'
    report_model = MessageReport

    def get_success_url(self):
        return reverse('chat_room', kwargs={'thread_id': self.target_object.thread_id})

    def form_valid(self, form):
        # 1. Закачаме докладваното съобщение и изпращача към инстанцията ПРЕДИ запазване
        form.instance.message = self.target_object
        form.instance.sender = self.request.user

        # 2. Вече можем безопасно да запишем обекта в базата данни
        self.object = form.save()
        report = self.object
        reported_message = self.target_object

        # 3. Извличаме контекстните съобщения
        before_messages = Message.objects.filter(
            thread=reported_message.thread,
            timestamp__lt=reported_message.timestamp
        ).order_by('-timestamp')[:10]

        after_messages = Message.objects.filter(
            thread=reported_message.thread,
            timestamp__gt=reported_message.timestamp
        ).order_by('timestamp')[:10]

        # 4. Записваме ги в ManyToMany полето
        report.context_messages.add(*before_messages, *after_messages, reported_message)

        # 5. Връщаме JSON отговор при AJAX заявка
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Докладът е изпратен успешно.'})

        return super(BaseCreateReportView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return super().form_invalid(form)


class CreateMessageAppeal(BaseCreateAppealView):
    template_name = 'chat/forms/create_message_appeal.html'
    model_to_appeal = Message
    object_target_field = 'message'
    appeal_model = MessageAppeal

    def get_success_url(self):
        return reverse('home')

from django.views.generic import ListView
from .models import MessageReport

class MessageReportListView(EditorOrSuperuserRequiredMixin, ListView):
    model = MessageReport
    template_name = 'chat/message_report_list.html'
    context_object_name = 'reports'
    ordering = ['-timestamp']
    paginate_by = 20


from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse
from django.http import HttpResponseForbidden


class UpdateMessage(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = UpdateMessageForm
    template_name = 'chat/forms/update_message_form.html'

    def get_success_url(self):
        return reverse('chat_room', kwargs={'thread_id': self.object.thread_id}) + "#message-" + str(self.object.id)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if (request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or
                (request.user == self.get_object().sender and not (
                        self.object.is_deleted_due_to_violation or self.object.is_deleted_due_to_ban))):
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    # 🟢 ДОБАВЕТЕ ТОЗИ МЕТОД:
    def form_valid(self, form):
        response = super().form_valid(form)

        # Ако заявката е AJAX (от JavaScript fetch)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'id': self.object.id,
                'text': self.object.text,  # Проверете дали полето за текст във вашия модел се казва 'text'
                'file_url': self.object.file.url if hasattr(self.object, 'file') and self.object.file else None
            })

        return response

    # 🔴 ЗА AJAX ГРЕШКИ (Ако формата не е валидна):
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
        return response

class DeleteMessage(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'chat/forms/delete_message_form.html'


    def get_success_url(self):
        return reverse('chat_room', kwargs={'thread_id': self.object.thread_id})

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if (request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or
                (request.user == self.get_object().sender and not (self.object.is_deleted_due_to_violation or self.object.is_deleted_due_to_ban))):
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

class DeleteMessageDueToViolation(DeleteContentDueToViolationBase):
    model = Message

    def get_success_url(self):
        return reverse('all_reported_messages')


class RestoreMessageFromViolation(RestoreContentFromViolationBase):
    model = Message

    def get_success_url(self):
        return reverse('all_reported_messages')



class UsersChats(LoginRequiredMixin, ListView):
    model = Thread
    template_name = 'chat/users_chats.html'
    context_object_name = 'threads'
    paginate_by = 20

    def get_queryset(self):
        return Thread.objects.filter(
            users=self.request.user
        ).annotate(
            latest_message_time=Max('message__timestamp')
        ).order_by('-latest_message_time')