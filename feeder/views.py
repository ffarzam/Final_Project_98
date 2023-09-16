from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.authentication import AccessTokenAuthentication
from .models import XmlLink, Channel
from .parsers import channel_parser_mapper, items_parser_mapper, item_model_mapper
from Permissions import IsSuperuser
from django.db import transaction, IntegrityError
from .serializer import ChannelListSerializer
from .utils import item_serializer_mapper, ChannelPagination, ItemsPagination


# Create your views here.


class CreateChannelAndItems(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsSuperuser,)

    def post(self, request):

        xml_link = request.data['xml_link']
        xml_link_qs = XmlLink.objects.filter(xml_link=xml_link)
        if xml_link_qs.exists():
            xml_link_obj = xml_link_qs.get()
            channel_qs = Channel.objects.filter(xml_link=xml_link_obj)
            if not channel_qs.exists():

                channel_parser = channel_parser_mapper(xml_link_obj.channel_parser)
                items_parser = items_parser_mapper(xml_link_obj.items_parser)
                channel_info = channel_parser(xml_link_obj.xml_link)
                ItemClass = item_model_mapper(xml_link_obj.rss_type.name)
                items_info = items_parser(xml_link_obj.xml_link)
                try:
                    with transaction.atomic():
                        channel = Channel.objects.create(xml_link=xml_link_obj, **channel_info)
                        items = (ItemClass(**item, channel=channel) for item in items_info)
                        ItemClass.objects.bulk_create(items)
                except IntegrityError as e:
                    return Response({"Message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

                return Response({"Message": "Channel and the Items Was Created"}, status=status.HTTP_201_CREATED)

            return Response({"Message": "Channel Already Exists"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"Message": "No Link Was Found"}, status=status.HTTP_404_NOT_FOUND)


class UpdateChannelAndItems(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsSuperuser,)

    def post(self, request):

        xml_link = request.data['xml_link']
        xml_link_qs = XmlLink.objects.filter(xml_link=xml_link)
        if xml_link_qs.exists():
            xml_link_obj = xml_link_qs.get()
            channel_qs = Channel.objects.filter(xml_link=xml_link_obj)
            if channel_qs.exists():
                channel = channel_qs.get()
                channel_parser = channel_parser_mapper(xml_link_obj.channel_parser)
                channel_info = channel_parser(xml_link_obj.xml_link)

                if channel.last_update != channel_info.get("last_update"):
                    channel.last_update = channel_info.get("last_update")
                    items_parser = items_parser_mapper(xml_link_obj.items_parser)
                    items_info = items_parser(xml_link_obj.xml_link)
                    ItemClass = item_model_mapper(xml_link_obj.rss_type.name)
                    try:
                        with transaction.atomic():
                            channel.save()
                            items = (
                                ItemClass(**item, channel=channel)
                                for item in items_info
                                if not ItemClass.objects.filter(guid=item.get("guid")).exists()
                            )
                            ItemClass.objects.bulk_create(items)
                    except IntegrityError as e:
                        return Response({"Message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

                    return Response({"Message": "Channel was Updated"}, status=status.HTTP_201_CREATED)

                return Response({"Message": "Channel is Already Updated"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"Message": "Channel Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"Message": "No Link Was Found"}, status=status.HTTP_404_NOT_FOUND)


class ChannelList(ListAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelListSerializer
    pagination_class = ChannelPagination


class ItemsList(APIView):
    def get(self, request, channel_id):
        try:
            channel = Channel.objects.get(id=channel_id)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

        ser_channel_data = ChannelListSerializer(channel)
        ItemClass = item_model_mapper(channel.xml_link.rss_type.name)
        all_items = ItemClass.objects.all()
        ItemSerializer = item_serializer_mapper(ItemClass.__name__)
        ser_items_data = ItemSerializer(all_items, many=True)
        data = {
            "channel": ser_channel_data.data,
            "items": ser_items_data.data
        }
        return Response(data, status=status.HTTP_200_OK)
