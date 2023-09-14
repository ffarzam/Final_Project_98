from django.contrib import admin
from .models import Like, Subscription, Comment, Bookmark

# Register your models here.

admin.site.register(Like)
admin.site.register(Subscription)
admin.site.register(Comment)
admin.site.register(Bookmark)
