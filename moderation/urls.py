from django.urls import path
from django.views.generic import TemplateView

from moderation.views import AllUsers, BanUser, DeleteBan, UpdateBan, AppealsView, \
    CreateBanAppeal, UserViolationsAndBansView

urlpatterns = [
    path('appeal_success/', TemplateView.as_view(template_name='moderation/appeal_success.html'), name='appeal_success'),
path("appeal_ban/<int:pk>/", CreateBanAppeal.as_view(), name='appeal_ban'),

    path(
        "violations/<int:user_id>/",
        UserViolationsAndBansView.as_view(),
        name="violations",
    ),    path('appeals/', AppealsView.as_view(), name='appeals'),
    path('users/', AllUsers.as_view(), name='all_users'),
    path('ban/<int:pk>/', BanUser.as_view(), name='ban_user'),
    path('unban/<int:pk>/', DeleteBan.as_view(), name='remove_ban'),
    path('edit_ban/<int:pk>/', UpdateBan.as_view(), name='edit_ban'),
]
