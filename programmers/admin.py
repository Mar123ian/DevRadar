from django.contrib import admin

from programmers.models import Programmer


# Register your models here.
@admin.register(Programmer)
class ProgrammerAdmin(admin.ModelAdmin):
    pass