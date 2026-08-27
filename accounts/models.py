from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
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
    email = models.EmailField(_("email address"), unique=True, error_messages={'unique': 'Потребител с този имейл вече съществува!'})

    objects = DevRadarUserManager()

    @property
    def is_programmer(self):
        return isinstance(self, ProgrammerUser)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_full_banned(self):

        ban = self.bans.filter(ban_type = 'FULL_BAN', active=True).last()
        if ban:
            return ban.permanent or (ban.duration and ban.duration + ban.start_date > timezone.now())

        return False

    def is_chat_banned(self):

        ban = self.bans.filter(ban_type='CHAT_BAN', active=True).last()
        if ban:
            return ban.permanent or (ban.duration and ban.duration + ban.start_date > timezone.now())

        return False

    def is_comments_banned(self):

        ban = self.bans.filter(ban_type = 'COMMENTS_BAN', active=True).last()
        if ban:
            return ban.permanent or (ban.duration and ban.duration + ban.start_date > timezone.now())

        return False

    def is_offer_service_banned(self):

        ban = self.bans.filter(ban_type = 'OFFER_SERVICE_BAN', active=True).last()
        if ban:
            return ban.permanent or (ban.duration and ban.duration + ban.start_date > timezone.now())

        return False

    def deleted_comments(self):
        return self.comments.filter(is_deleted_due_to_violation=True)


    def deleted_messages(self):
        return self.messages.filter(is_deleted_due_to_violation=True)

    def new_deleted_comments(self):
        return self.deleted_comments().filter(is_user_informed_about_violation=False)

    def new_deleted_messages(self):
        return self.deleted_messages().filter(is_user_informed_about_violation=False)

class ProgrammerUser(DevRadarUser):
    image = models.ImageField(upload_to='programmers/')

    phone_number = models.CharField(max_length=15,
                                    error_messages={'max_length': 'Максималната дължина е 15 символа!',})
                                                    # 'unique': 'Програмист с този тел. номер вече съществува!'
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            objects_with_that_name = self.__class__.objects.filter(slug=slugify(unidecode(self.get_full_name()))).count()


            if objects_with_that_name > 0:
                self.slug = slugify(unidecode(self.get_full_name()) + f"{objects_with_that_name + 1}")
            else:
                self.slug = slugify(unidecode(self.get_full_name()))

        super().save(*args, **kwargs)

    def deleted_services(self):
        return self.services.filter(is_deleted_due_to_violation=True)

    def new_deleted_services(self):
        return self.deleted_services().filter(is_user_informed_about_violation=False)

    def active_services(self):
        return self.services.filter(is_deleted_due_to_violation=False, is_deleted_due_to_ban=False)




