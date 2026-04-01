from django.urls import path, include

from comments.views import DeleteComment, UpdateComment

urlpatterns = [


        path('delete/<int:pk>/', DeleteComment.as_view(), name='delete_comment'),
        path('update/<int:pk>/', UpdateComment.as_view(), name='update_comment'),


]