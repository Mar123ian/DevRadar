from django.db import models
from django.utils.text import slugify

from core.mixins import CreatedAndUpdatedAtMixin


# Create your models here.
class CategoryBase(CreatedAndUpdatedAtMixin, models.Model):
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Type(CategoryBase):
    name = models.CharField(unique=True, max_length=100, error_messages={'max_length': 'Максималната дължина е 100 символа!', 'unique': 'Типът услуга вече съществува!'})
    description = models.TextField()
    image = models.ImageField(upload_to='categories/types/')

class Technology(CategoryBase):
    name = models.CharField(unique=True, max_length=100, error_messages={'max_length': 'Максималната дължина е 100 символа!', 'unique': 'Технологията вече съществува!'})
    image = models.ImageField(upload_to='categories/technologies/')



