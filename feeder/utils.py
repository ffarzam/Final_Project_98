from rest_framework.pagination import PageNumberPagination

from .serializer import EpisodeSerializer, NewsSerializer


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
