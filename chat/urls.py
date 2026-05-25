from django.conf.urls.static import static
from django.urls import path, include

from chat import views
from devradar import settings

urlpatterns = [
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('<int:thread_id>/', views.chat_room, name='chat_room'),
path("upload/", views.upload_file),
]
