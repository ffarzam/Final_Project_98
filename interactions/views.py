from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.authentication import AccessTokenAuthentication

from feeder.models import Channel
from feeder.parsers import item_model_mapper

from .models import Like


# Create your views here.


class LikeView(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        action = request.data.get("action")
        channel_id = request.data.get("channel_id")
        item_id = request.data.get("item_id")

        try:
            channel = Channel.objects.get(id=channel_id)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

        ItemClass = item_model_mapper(channel.xml_link.rss_type.name)

        try:
            item = ItemClass.objects.get(id=item_id)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

        content_type_obj = item.get_content_type_obj
        like_query = Like.objects.filter(content_type=content_type_obj, object_id=item.id, user=request.user)

        if action == "unlike" and like_query.exists():
            like_query.delete()

        elif action == "like" and not like_query.exists():
            Like.objects.create(content_object=item, user=request.user)

        count = item.number_of_likes

        return Response({'like_count': count}, status=status.HTTP_200_OK)