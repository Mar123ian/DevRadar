from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .models import Thread
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

from django.http import JsonResponse

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