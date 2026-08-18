from django.db import models

from core.managers import NonDeletedManager
from moderation.mixins import ViolationSoftDeleteMixin
from moderation.models import BaseReport, BaseAppeal


# Create your models here.
class Comment(ViolationSoftDeleteMixin, models.Model):
    author = models.ForeignKey('accounts.DevRadarUser', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='comments')
    is_deleted = models.BooleanField(default=False)


    class Meta:
        ordering = ['-created_at', 'id']

    def __str__(self):
        #return f"{self.author} - {self.content}"
        return f"{self.content}"

class CommentReport(BaseReport):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports')

class CommentAppeal(BaseAppeal):
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name='violation_appeal')

