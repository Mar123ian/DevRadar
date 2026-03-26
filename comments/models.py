from django.db import models

# Create your models here.
class Comment(models.Model):
    author = models.ForeignKey('accounts.DevRadarUser', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='comments')

    class Meta:
        ordering = ['-created_at', 'id']

    def __str__(self):
        #return f"{self.author} - {self.content}"
        return f"{self.content}"

