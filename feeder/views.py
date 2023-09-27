from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Q, F

from .models import Channel, Episode, News
from .parsers import item_model_mapper
from .serializer import ChannelSerializer, EpisodeSerializer, NewsSerializer
from .utils import item_serializer_mapper, ChannelPagination, ItemsPagination, search_counter

from accounts.authentication import AccessTokenAuthentication, RefreshTokenAuthentication
from Permissions import IsSuperuser

from . import tasks


# Create your views here.


class UpdateChannelAndItems(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsSuperuser,)

    def post(self, request):

        xml_link = request.data.get('xml_link')
        if xml_link:
            tasks.update_single_rss.delay(xml_link)
        else:
            tasks.update_all_rss.delay()

        return Response({"Update will be done soon"}, status=status.HTTP_200_OK)


class ChannelList(ListAPIView):
    serializer_class = ChannelSerializer
    pagination_class = ChannelPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['title']

    def get_queryset(self):

        filter_query = self.request.query_params.get("filter")
        if filter_query:
            queryset = Channel.objects.select_related("xml_link").prefetch_related("xml_link__categories").filter(
                xml_link__categories__name=filter_query)
        else:
            queryset = Channel.objects.prefetch_related("searchcount_set").annotate(
                search_count=F("searchcount__count")).order_by(F("search_count").desc(nulls_last=True))
        return queryset


class ItemsList(GenericAPIView):  # or ListAPIView
    pagination_class = ItemsPagination  # LimitOffsetPagination???

    def get(self, request, channel_id):
        try:
            channel = Channel.objects.get(id=self.kwargs["channel_id"])
            ItemClass = item_model_mapper(channel.xml_link.rss_type.name)
            all_items = ItemClass.objects.filter(channel=channel)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        paginator = self.pagination_class()
        paginated_items = paginator.paginate_queryset(queryset=all_items, request=request, view=self)
        ItemSerializer = item_serializer_mapper(ItemClass.__name__)
        try:
            user, _ = RefreshTokenAuthentication().authenticate(request)
            request.user = user
        except:
            pass

        ser_items_data = ItemSerializer(paginated_items, many=True, context={"request": request})
        return Response(ser_items_data.data, status=status.HTTP_200_OK)


class GetChannel(RetrieveAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer


class GetItem(APIView):

    def get(self, request, channel_id, item_id):
        try:
            channel = Channel.objects.get(id=channel_id)
            ItemClass = item_model_mapper(channel.xml_link.rss_type.name)
            item = ItemClass.objects.get(id=item_id)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

        ItemSerializer = item_serializer_mapper(ItemClass.__name__)
        ser_item = ItemSerializer(item, context={"request": request})

        return Response(ser_item.data, status=status.HTTP_200_OK)


class SearchView(APIView):
    def get(self, request):
        search_query = request.query_params["search"]

        channel_search_results = Channel.objects.filter(
            Q(title__icontains=search_query) | Q(subtitle__icontains=search_query) | Q(
                description__icontains=search_query)).distinct()

        episode_search_results = Episode.objects.select_related("channel").filter(
            Q(title__icontains=search_query) | Q(subtitle__icontains=search_query) | Q(
                description__icontains=search_query)).distinct()

        news_search_results = News.objects.select_related("channel").filter(Q(title__icontains=search_query)).distinct()

        channel_id_set = set(map(lambda x: x[0], channel_search_results.values_list("id")))
        channel_id_set_for_episode_search = set(map(lambda x: x[0], episode_search_results.values_list("channel")))
        channel_id_set_for_news_search = set(map(lambda x: x[0], episode_search_results.values_list("channel")))

        channel_id_set = channel_id_set | channel_id_set_for_episode_search | channel_id_set_for_news_search
        search_counter(channel_id_set)

        context = {"request": request}
        channel_search_results_serialized = ChannelSerializer(channel_search_results, many=True, context=context)
        episode_search_results_serialized = EpisodeSerializer(episode_search_results, many=True, context=context)
        news_search_results_serialized = NewsSerializer(news_search_results, many=True, context=context)

        data = {
            "channel_search_results": channel_search_results_serialized.data,
            "episode_search_results": episode_search_results_serialized.data,
            "news_search_results": news_search_results_serialized.data
        }

        return Response(data, status=status.HTTP_200_OK)
