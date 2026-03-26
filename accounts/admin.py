from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import DevRadarUser, ProgrammerUser
from services.models import Service


# Register your models here.
@admin.register(DevRadarUser)
class DevRadarUserAdmin(UserAdmin):
    pass

@admin.register(ProgrammerUser)
class ProgrammerUserAdmin(UserAdmin):
    pass
