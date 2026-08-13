from django.urls import path, include

from comments.views import DeleteComment, UpdateComment, CreateCommentReport, CommentReportListView, \
    RestoreCommentFromViolation, DeleteCommentDueToViolation

urlpatterns = [

path("delete_comment_due_to_violation/<int:pk>/", DeleteCommentDueToViolation.as_view(), name='delete_comment_due_to_violation'),
    path("restore_comment_from_violation/<int:pk>/", RestoreCommentFromViolation.as_view(),
         name='restore_comment_from_violation'),
        path('delete/<int:pk>/', DeleteComment.as_view(), name='delete_comment'),
        path('update/<int:pk>/', UpdateComment.as_view(), name='update_comment'),
path("report_comment/<int:pk>/", CreateCommentReport.as_view(), name='report_comment'),
    path("all_reported_comments/", CommentReportListView.as_view(), name='all_reported_comments'),


]