from django.contrib import admin

from moderation.models import Ban, BanAppeal


# Register your models here.
@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    pass

@admin.register(BanAppeal)
class BanAppealAdmin(admin.ModelAdmin):
    pass
