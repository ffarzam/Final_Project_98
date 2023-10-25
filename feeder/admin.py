from django.contrib import admin

from .models import XmlLink, Channel, Episode, Category, Type, News, SearchCount


# Register your models here.

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("id", 'title', 'last_update', "xml_link", "language",)
    list_filter = ('title', 'last_update', "xml_link", "language",)
    search_fields = ("id", 'title__istartswith',)


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("id", 'title', 'published_date', "channel")
    list_filter = ('title', 'published_date', "channel")
    search_fields = ("id", 'title__istartswith', "channel__title__istartswith")


admin.site.register(XmlLink)
admin.site.register(News)
admin.site.register(Category)
admin.site.register(Type)
admin.site.register(SearchCount)
