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
from moderation.views import BaseCreateReportView, DeleteContentDueToViolationBase, RestoreContentFromViolationBase

from .forms import UpdateMessageForm
from .models import Thread, MessageReport
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

@login_required
def chat_room(request, thread_id):


    thread = get_object_or_404(Thread, id=thread_id, users=request.user.id)


    messages = Message.objects.filter(thread=thread).order_by("timestamp")

    return render(request, "chat_room.html", {
        "thread": thread,
        "messages": messages
    })

from django.views.generic.edit import FormView, BaseDeleteView
from django.urls import reverse
from django.shortcuts import get_object_or_404

class CreateMessageReport(BaseCreateReportView):
    template_name = 'chat/forms/create_message_report.html'
    model_to_report = Message
    object_target_field = 'message'
    report_model = MessageReport

    def get_success_url(self):
        return reverse('chat_room', kwargs={'thread_id': self.target_object.thread_id})

    def form_valid(self, form):
        response = super().form_valid(form)
        report = form.instance
        reported_message = self.target_object

        # Взимаме до 10 съобщения преди докладваното
        before_messages = Message.objects.filter(
            thread=reported_message.thread,
            timestamp__lt=reported_message.timestamp
        ).order_by('-timestamp')[:10]

        # Взимаме до 10 съобщения след докладваното
        after_messages = Message.objects.filter(
            thread=reported_message.thread,
            timestamp__gt=reported_message.timestamp
        ).order_by('timestamp')[:10]

        # Записваме намерените съобщения в ManyToMany полето
        report.context_messages.add(*before_messages, *after_messages)

        return response

from django.views.generic import ListView
from .models import MessageReport

class MessageReportListView(EditorOrSuperuserRequiredMixin, ListView):
    model = MessageReport
    template_name = 'chat/message_report_list.html'
    context_object_name = 'reports'
    ordering = ['-timestamp']


class UpdateMessage(LoginRequiredMixin, UpdateView):

    model = Message
    form_class = UpdateMessageForm
    template_name = 'chat/forms/update_message_form.html'

    def get_success_url(self):
        return reverse('chat_room', kwargs={'thread_id': self.object.thread_id})+"#message-"+str(self.object.id)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if (request.user.groups.filter(name='Editors').exists() or request.user.is_superuser or
                (request.user == self.get_object().sender and not (
                        self.object.is_deleted_due_to_violation or self.object.is_deleted_due_to_ban))):
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

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



class UsersChats(ListView):
    model = Thread
    template_name = 'chat/users_chats.html'
    context_object_name = 'threads'

    def get_queryset(self):
        return Thread.objects.filter(
            users=self.request.user
        ).annotate(
            latest_message_time=Max('message__timestamp')
        ).order_by('-latest_message_time')