from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetDoneView, PasswordResetCompleteView
from django.urls import path
from django.views.generic import TemplateView

from accounts.views import RegisterProgrammerUserView, RegisterDevRadarUserView, UpdateDevRadarUser, DeleteDevRadarUser

urlpatterns = [
    path('profile/', TemplateView.as_view(template_name='accounts/profile.html'), name='profile'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('register-programmer/', RegisterProgrammerUserView.as_view(), name='register_programmer'),
    path('register/', TemplateView.as_view(template_name="accounts/register.html"), name='register'),
    path('register-user/', RegisterDevRadarUserView.as_view(), name='register_user'),
    path('logout/', LogoutView.as_view(http_method_names=['post']), name='logout'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('update/<int:pk>/', UpdateDevRadarUser.as_view(), name='update_user'),
    path('delete/<int:pk>/', DeleteDevRadarUser.as_view(), name='delete_user'),

]