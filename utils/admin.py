from django.contrib import admin

from .models import *
# Register your models here.


class ContactusAdmin(admin.ModelAdmin):
    list_display = ("first_name",  "id")
    search_fields = ("first_name",)


admin.site.register(Contactus, ContactusAdmin)