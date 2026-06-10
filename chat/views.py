from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView

from .forms import MessageReportForm
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

class CreateMessageReport(FormView):
    template_name = 'chat/forms/create_message_report.html'
    form_class = MessageReportForm

    def dispatch(self, request, *args, **kwargs):
        self.message = get_object_or_404(Message, pk=kwargs['pk'])
        self.thread_id = self.message.thread_id
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        message_report = form.save(commit=False)
        message_report.sender = self.request.user
        message_report.message = self.message
        message_report.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('chat_room', kwargs={'thread_id': self.thread_id})

from django.views.generic import ListView
from .models import MessageReport

class MessageReportListView(ListView):
    model = MessageReport
    template_name = 'chat/message_report_list.html'
    context_object_name = 'reports'
    ordering = ['-timestamp']

    # TODO permissions not dispatch
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Editors').exists() or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()