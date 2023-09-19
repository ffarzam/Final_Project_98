import itertools

from django.db.models import Max, F, Subquery, Q
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.authentication import AccessTokenAuthentication

from feeder.models import Channel
from feeder.parsers import item_model_mapper

from .models import Like, Recommendation
from feeder.serializer import ChannelSerializer


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
            categories = channel.xml_link.categories.all()
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
            for category in categories:
                recommendation_obj, created = Recommendation.objects.get_or_create(user=request.user, category=category)
                recommendation_obj.count -= 1
                recommendation_obj.save()

        elif action == "like" and not like_query.exists():
            Like.objects.create(content_object=item, user=request.user)
            for category in categories:
                recommendation_obj, created = Recommendation.objects.get_or_create(user=request.user, category=category)
                recommendation_obj.count += 1
                recommendation_obj.save()

        count = item.number_of_likes

        return Response({'like_count': count}, status=status.HTTP_200_OK)


class RecommendationView(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        max_count = Recommendation.objects.aggregate(max_count=Max("count"))["max_count"]
        recommendation_query = Recommendation.objects.filter(user=user, count=max_count)
        lst = []
        for item in recommendation_query:
            channel = Channel.objects.filter(xml_link__categories=item.category)
            lst.append(list(channel))

        flatList = set(sum(lst, []))
        ser_data = ChannelSerializer(flatList, many=True)

        return Response(ser_data.data, status=status.HTTP_200_OK)
