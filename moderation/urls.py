from django.urls import path

from moderation.views import AllUsers, BanUser, DeleteBan, UpdateBan, user_violations_and_bans_view, AppealsView, \
    CreateBanAppeal

urlpatterns = [
path("appeal_ban/<int:pk>/", CreateBanAppeal.as_view(), name='appeal_ban'),

    path('violations/', user_violations_and_bans_view, name='violations'),
    path('appeals/', AppealsView.as_view(), name='appeals'),
    path('users/', AllUsers.as_view(), name='all_users'),
    path('ban/<int:pk>/', BanUser.as_view(), name='ban_user'),
    path('unban/<int:pk>/', DeleteBan.as_view(), name='remove_ban'),
    path('edit_ban/<int:pk>/', UpdateBan.as_view(), name='edit_ban'),
]
