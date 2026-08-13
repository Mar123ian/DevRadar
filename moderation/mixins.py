from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class EditorOrSuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Editors').exists()

    def handle_no_permission(self):
        raise PermissionDenied


from django.db import models

class ViolationSoftDeleteMixin(models.Model):
    is_deleted_due_to_ban = models.BooleanField(default=False)

    is_deleted_due_to_violation = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Оказва дали обектът е премахнат заради нарушение."
    )
    last_violation_info = models.JSONField(
        blank=True,
        null=True,
        help_text="Детайли за последното нарушение (напр. причина, модератор, дата)."
    )

    is_user_informed_about_violation = models.BooleanField(
        default=False,
    )

    class Meta:
        abstract = True
