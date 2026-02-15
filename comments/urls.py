from django.urls import path

from comments.views import CreateComment

urlpatterns = [
    path('create/', CreateComment.as_view(), name='create_comment'),
]