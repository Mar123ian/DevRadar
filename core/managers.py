from django.db import models

import services


class NonDeletedManager(models.Manager):
    def get_queryset(self):

        queryset = super().get_queryset().filter(is_deleted=False)

        if self.model.__name__ in  ('Service', 'Comment'):
            queryset = queryset.filter(is_deleted_due_to_ban=False)

        return queryset