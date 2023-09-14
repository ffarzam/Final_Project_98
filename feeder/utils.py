from .serializer import EpisodeListSerializer, NewsListSerializer


def item_serializer_mapper(item_class_name):
    mapper = {
        "Episode": EpisodeListSerializer,
        "News": NewsListSerializer,
    }

    return mapper[item_class_name]
