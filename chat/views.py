from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView

from moderation.mixins import EditorOrSuperuserRequiredMixin
from moderation.views import BaseCreateReportView
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

from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import get_object_or_404

class CreateMessageReport(BaseCreateReportView):
    template_name = 'chat/forms/create_message_report.html'
    model_to_report = Message
    object_target_field = 'message'
    report_model = MessageReport

    def get_success_url(self):
        return reverse('chat_room', kwargs={'thread_id': self.target_object.thread_id})

from django.views.generic import ListView
from .models import MessageReport

class MessageReportListView(EditorOrSuperuserRequiredMixin, ListView):
    model = MessageReport
    template_name = 'chat/message_report_list.html'
    context_object_name = 'reports'
    ordering = ['-timestamp']