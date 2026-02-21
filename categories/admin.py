from django.contrib import admin

from categories.models import Technology, Type


# Register your models here.
@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    pass