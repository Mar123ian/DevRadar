from django.db import models
from django.utils.text import slugify

from core.mixins import CreatedAndUpdatedAtMixin


# Create your models here.
class Programmer(CreatedAndUpdatedAtMixin, models.Model):
    first_name  = models.CharField(max_length=100, error_messages={'max_length': 'Максималната дължина е 100 символа!'})
    image = models.ImageField(upload_to='programmers/')
    last_name   = models.CharField(max_length=100, error_messages={'max_length': 'Максималната дължина е 100 символа!'})
    email = models.EmailField(unique=True, error_messages={'unique': 'Програмист с този имейл вече съществува!'})
    phone_number = models.CharField(unique=True, max_length=15, error_messages={'max_length': 'Максималната дължина е 15 символа!', 'unique': 'Програмист с този тел. номер вече съществува!'})
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.get_full_name())
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"



