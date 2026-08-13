from django.conf import settings
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

from core.managers import NonDeletedManager
from core.mixins import CreatedAndUpdatedAtMixin
from moderation.mixins import ViolationSoftDeleteMixin
from moderation.models import BaseReport


# Create your models here.
class Service(ViolationSoftDeleteMixin, CreatedAndUpdatedAtMixin, models.Model):
    name = models.CharField(max_length=255, error_messages={'max_length': 'Максималната дължина е 255 символа!'})
    programmer = models.ForeignKey('accounts.ProgrammerUser', on_delete=models.CASCADE, related_name='services')
    description = models.TextField()
    image = models.ImageField(upload_to='services/')
    slug = models.SlugField(unique=True, blank=True)
    type = models.ForeignKey('categories.Type', on_delete=models.CASCADE, related_name='services')
    technologies = models.ManyToManyField('categories.Technology', related_name='services')
    min_price = models.DecimalField(max_digits=10, decimal_places=2, error_messages={'max_digits': 'Максималната дължина е 10 цифри!', 'decimal_places': 'Максималната дължина след десетичната запетая е 2 цифри!'})
    max_price = models.DecimalField(max_digits=10, decimal_places=2, error_messages={'max_digits': 'Максималната дължина е 10 цифри!', 'decimal_places': 'Максималната дължина след десетичната запетая е 2 цифри!'})
    is_deleted = models.BooleanField(default=False)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'programmer'], name='unique_service_for_programmer', violation_error_message='Този програмист вече е предложил същата услуга!'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.programmer.slug + ' ' + self.name))
        super().save(*args, **kwargs)

    def active_comments(self):
        return self.comments.filter(is_deleted_due_to_violation=False, is_deleted_due_to_ban=False)

    def active_services(self):
        return self.objects.filter(is_deleted_due_to_violation=False)


class ServiceReport(BaseReport):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reports')