from django.contrib.contenttypes.models import ContentType
from rest_framework.pagination import PageNumberPagination

from .serializer import EpisodeSerializer, NewsSerializer

from interactions.models import Like


def item_serializer_mapper(item_class_name):
    mapper = {
        "Episode": EpisodeSerializer,
        "News": NewsSerializer,
    }

    return mapper[item_class_name]


class ChannelPagination(PageNumberPagination):
    page_size = 8


class ItemsPagination(PageNumberPagination):
    page_size = 20


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
