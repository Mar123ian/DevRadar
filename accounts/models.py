from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from unidecode import unidecode


# Create your models here.
from django.contrib.auth.models import UserManager

class DevRadarUserManager(UserManager, PolymorphicManager):
    pass

class DevRadarUser(PolymorphicModel,AbstractUser):

    first_name = models.CharField(_("first name"), max_length=150, error_messages={'max_length': 'Максималната дължина е 100 символа!'})
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    favourites = models.ManyToManyField('services.Service', related_name='users', blank=True)
    email = models.EmailField(_("email address"), unique=True, error_messages={'unique': 'Програмист с този имейл вече съществува!'})

    objects = DevRadarUserManager()



    def __str__(self):
        return f"{self.first_name} {self.last_name}"



    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class ProgrammerUser(DevRadarUser):
    image = models.ImageField(upload_to='programmers/')

    phone_number = models.CharField(unique=True, max_length=15,
                                    error_messages={'max_length': 'Максималната дължина е 15 символа!',
                                                    'unique': 'Програмист с този тел. номер вече съществува!'})
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            objects_with_that_name = self.__class__.objects.filter(slug=slugify(unidecode(self.get_full_name()))).count()


            if objects_with_that_name > 0:
                self.slug = slugify(unidecode(self.get_full_name()) + f"{objects_with_that_name + 1}")
            else:
                self.slug = slugify(unidecode(self.get_full_name()))

        super().save(*args, **kwargs)



