from django.db import models

# Create your models here.
class Comment(models.Model):
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"{self.author} - {self.content}"

