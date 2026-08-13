from django.conf.urls.static import static
from django.urls import path, include

from chat import views
from chat.views import CreateMessageReport, MessageReportListView, DeleteMessage, UpdateMessage, UsersChats, \
    DeleteMessageDueToViolation, RestoreMessageFromViolation
from devradar import settings

urlpatterns = [
    path("chats/", UsersChats.as_view(), name='users_chats'),
    path("delete_message_due_to_violation/<int:pk>/", DeleteMessageDueToViolation.as_view(), name='delete_message_due_to_violation'),
    path("restore_message_from_violation/<int:pk>/", RestoreMessageFromViolation.as_view(),
         name='restore_message_from_violation'),

    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('<int:thread_id>/', views.chat_room, name='chat_room'),
path("upload/", views.upload_file),
    path("report_message/<int:pk>/", CreateMessageReport.as_view(), name='report_message'),
    path("all_reported_messages/", MessageReportListView.as_view(), name='all_reported_messages'),
    path('delete/<int:pk>/', DeleteMessage.as_view(), name='delete_message'),
    path('update/<int:pk>/', UpdateMessage.as_view(), name='update_message'),
]
