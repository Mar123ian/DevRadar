import random

from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

from core.mixins import CreatedAndUpdatedAtMixin


# Create your models here.
class CategoryBase(CreatedAndUpdatedAtMixin, models.Model):
    slug = models.SlugField(unique=True, blank=True)
    is_deleted = models.BooleanField(default=False)


    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        
        if not self.pk or (self.name != self.__class__.objects.filter(pk=self.pk).first().name):
            
            count = 0
            base_slug = slugify(unidecode(self.name))

            while True:
                slug = f"{base_slug}{count + 1}" if count > 0 else base_slug

                if self.__class__.objects.exclude(pk=self.pk).filter(slug=slug).exists():

                    count += 1
                else:
                    self.slug = slug
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Type(CategoryBase):
    name = models.CharField(unique=True, max_length=100, error_messages={'max_length': 'Максималната дължина е 100 символа!', 'unique': 'Типът услуга вече съществува!'})
    description = models.TextField()
    image = models.ImageField(upload_to='categories/types/')

    def active_services(self):
        return self.services.filter(is_deleted_due_to_violation=False, is_deleted_due_to_ban=False)

    class Meta:
        ordering = ['id']


class Technology(CategoryBase):
    name = models.CharField(unique=True, max_length=100, error_messages={'max_length': 'Максималната дължина е 100 символа!', 'unique': 'Технологията вече съществува!'})
    image = models.ImageField(upload_to='categories/technologies/')

    class Meta:
        ordering = ['name']



