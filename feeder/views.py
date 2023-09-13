from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.authentication import CustomJWTAuthentication
from .models import XmlLink, Channel
from .parsers import channel_parser_mapper, items_parser_mapper, item_model_mapper
from Permissions import IsSuperuser


# Create your views here.


class CreateChannelAndItems(APIView):
    authentication_classes = (CustomJWTAuthentication,)
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
                channel = Channel.objects.create(xml_link=xml_link_obj, **channel_info)

                ItemClass = item_model_mapper(xml_link_obj.rss_type.name)

                items_info = items_parser(xml_link_obj.xml_link)
                items = (ItemClass(**item, channel=channel) for item in items_info)
                ItemClass.objects.bulk_create(items)

                return Response({"Message": "Channel and the Items Was Created"}, status=status.HTTP_201_CREATED)

            else:
                return Response({"Message": "Channel Already Exists"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"Message": "No Link Was Found"}, status=status.HTTP_404_NOT_FOUND)
