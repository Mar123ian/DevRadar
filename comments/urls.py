from django.urls import path, include

from comments.views import DeleteComment, UpdateComment, CreateCommentReport, CommentReportListView

urlpatterns = [


        path('delete/<int:pk>/', DeleteComment.as_view(), name='delete_comment'),
        path('update/<int:pk>/', UpdateComment.as_view(), name='update_comment'),
path("report_comment/<int:pk>/", CreateCommentReport.as_view(), name='report_comment'),
    path("all_reported_comments/", CommentReportListView.as_view(), name='all_reported_comments'),


]