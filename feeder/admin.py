from django.contrib import admin

from .models import XmlLink, Channel, Episode, Category, Type

# Register your models here.


admin.site.register(XmlLink)
admin.site.register(Channel)
admin.site.register(Episode)
admin.site.register(Category)
admin.site.register(Type)
