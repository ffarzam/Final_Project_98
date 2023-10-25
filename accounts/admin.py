from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from . import models


# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = models.CustomUser
    list_display = ('username', 'email', "is_staff", "is_active", "is_superuser",)
    list_filter = ('username', 'email', "is_staff", "is_active", "is_superuser",)
    fieldsets = (
        (None, {"fields": ('username', 'email', "password", "is_account_enable")}),
        ("Permissions",
         {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                'username', 'email', "password1", "password2", "is_account_enable"
                                                               "is_active", "is_staff", "is_superuser", "groups",
                "user_permissions"
            )}
         ),
    )
    search_fields = ('username__istartswith', 'email__istartswith')


admin.site.site_header = 'RSS Feed Management'
admin.site.site_title = 'RSS Feed Management'
admin.site.index_title = 'Welcome to Admin Panel'

admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.Notification)
admin.site.register(models.UserNotifications)
admin.site.register(models.UserLastActivity)
