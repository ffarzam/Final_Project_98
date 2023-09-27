from django.contrib.contenttypes.models import ContentType

from interactions.models import Bookmark, Like


class ItemsMixin:
    @property
    def number_of_likes(self):
        content_type_obj = self.get_content_type_obj
        likes_count = Like.objects.filter(content_type=content_type_obj, object_id=self.id).count()
        return likes_count

    @property
    def get_content_type_obj(self):
        return ContentType.objects.get(model=self.__class__.__name__.lower())

    def __str__(self):
        return f'RSS Feed: {self.channel} || {self.__class__.__name__}: {self.title}'


class BookmarkMixin:

    def get_is_bookmarked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Bookmark.objects.filter(user=user,
                                           content_type=ContentType.objects.get(model=obj.__class__.__name__.lower()),
                                           object_id=obj.id).exists()
        return False


class LikeMixin:
    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Like.objects.filter(user=user,
                                       content_type=ContentType.objects.get(model=obj.__class__.__name__.lower()),
                                       object_id=obj.id).exists()
        return False

    def get_liked_count(self, obj):
        return obj.number_of_likes
