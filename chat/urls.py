from django.conf.urls.static import static
from django.urls import path, include

from chat import views
from chat.views import CreateMessageReport, MessageReportListView
from devradar import settings

urlpatterns = [
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('<int:thread_id>/', views.chat_room, name='chat_room'),
path("upload/", views.upload_file),
    path("report_message/<int:pk>/", CreateMessageReport.as_view(), name='report_message'),
    path("all_reported_messages/", MessageReportListView.as_view(), name='all_reported_messages'),
]
