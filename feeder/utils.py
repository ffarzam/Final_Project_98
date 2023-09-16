from rest_framework.pagination import PageNumberPagination

from .serializer import EpisodeListSerializer, NewsListSerializer


def item_serializer_mapper(item_class_name):
    mapper = {
        "Episode": EpisodeListSerializer,
        "News": NewsListSerializer,
    }

    return mapper[item_class_name]


class ChannelPagination(PageNumberPagination):
    page_size = 8


class ItemsPagination(PageNumberPagination):
    page_size = 20
