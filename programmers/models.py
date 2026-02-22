from django.db import models, IntegrityError
from django.utils.text import slugify
from unidecode import unidecode

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
            objects_with_that_name = self.__class__.objects.filter(first_name=self.first_name,
                                                                   last_name=self.last_name).count()

            if objects_with_that_name > 0:
                self.slug = slugify(unidecode(self.get_full_name()) + f"{objects_with_that_name + 1}")
            else:
                self.slug = slugify(unidecode(self.get_full_name()))



        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"



