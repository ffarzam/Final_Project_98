from django.contrib import admin
from .models import Like, Comment, Bookmark, Recommendation

# Register your models here.

admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Bookmark)
admin.site.register(Recommendation)
