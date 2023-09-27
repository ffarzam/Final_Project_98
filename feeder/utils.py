from rest_framework.pagination import PageNumberPagination

from .models import SearchCount
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


def search_counter(channel_id_set):
    for channel_id in channel_id_set:
        search_count_obj, created = SearchCount.objects.get_or_create(channel_id=channel_id)
        search_count_obj.count += 1
        search_count_obj.save()
