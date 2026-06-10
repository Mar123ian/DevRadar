from django.db import models

from core.managers import NonDeletedManager


# Create your models here.
class Comment(models.Model):
    author = models.ForeignKey('accounts.DevRadarUser', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='comments')
    is_deleted = models.BooleanField(default=False)
    is_deleted_due_to_ban = models.BooleanField(default=False)


    objects = NonDeletedManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-created_at', 'id']

    def __str__(self):
        #return f"{self.author} - {self.content}"
        return f"{self.content}"

