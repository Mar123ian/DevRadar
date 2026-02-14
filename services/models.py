from django.db import models
from django.utils.text import slugify


# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    categories = models.ManyToManyField('categories.Category', related_name='services')
    from_price = models.DecimalField(max_digits=10, decimal_places=2)
    to_price = models.DecimalField(max_digits=10, decimal_places=2)
    comments = models.ForeignKey('comments.Comment', on_delete=models.CASCADE, related_name='service')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

