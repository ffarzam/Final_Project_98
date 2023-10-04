from django.contrib import admin

from . import models

# Register your models here.


admin.site.register(models.CustomUser)
admin.site.register(models.Notification)
admin.site.register(models.UserNotifications)
