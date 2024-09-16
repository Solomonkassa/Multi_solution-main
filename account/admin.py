from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Trainee, APIKey, Preference


class BaseUserAdmin(UserAdmin):
    """
    Base admin configuration for User model.
    """
    list_display = (
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "is_phone_verified",
        "password",
    )
    list_filter = ("is_staff", "is_superuser", "date_joined")
    search_fields = ("phone_number", "first_name", "last_name")



class TraineeAdmin(admin.ModelAdmin):
    """
    Admin configuration for Student model.
    """
    def get_queryset(self, request):
        return Trainee.objects.filter(is_trainee=True)
    
    list_display = (
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "is_phone_verified",
    )
    list_filter = ("country", "city")
    search_fields = ("phone_number", "first_name", "last_name")
    
class APIKeyAdmin(admin.ModelAdmin):
    """
    Admin configuration for APIKey model.
    """
    list_display = ("key", "name", "suspended")
    list_filter = ("name",)
    search_fields = ("key", "name")
    
class PreferenceAdmin(admin.ModelAdmin):
    """
    Admin configuration for Preference model.
    """
    list_display = ("tg_id", "contact", "bank", "language")
    list_filter = ("tg_id",)
    search_fields = ("language", "bank")


admin.site.register(User, BaseUserAdmin)
admin.site.register(Trainee, TraineeAdmin)
admin.site.register(APIKey, APIKeyAdmin)
admin.site.register(Preference, PreferenceAdmin)


