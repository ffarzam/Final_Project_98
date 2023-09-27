from django.contrib.contenttypes.models import ContentType
from django.db.models import Max

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.authentication import AccessTokenAuthentication

from .models import Like, Recommendation, Comment, Bookmark
from .seializers import CommentSerializer
from .tasks import create_comment
from .utils import CommentsPagination, recommendation_counter, UserLikeListPagination

from feeder.models import Channel, Episode, News
from feeder.parsers import item_model_mapper
from feeder.serializer import EpisodeSerializer, NewsSerializer, ChannelSerializer
from feeder.utils import ChannelPagination, item_serializer_mapper

from feeder.utils import ItemsPagination


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
            ItemClass = item_model_mapper(channel.xml_link.rss_type.name)
            item = ItemClass.objects.get(id=item_id)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

        content_type_obj = item.get_content_type_obj
        like_query = Like.objects.filter(content_type=content_type_obj, object_id=item.id, user=request.user)

        if action == "unlike" and like_query.exists():
            like_query.delete()
            recommendation_counter(request.user, categories)
            message = "Like Undone"

        elif action == "like" and not like_query.exists():
            Like.objects.create(content_object=item, user=request.user)
            recommendation_counter(request.user, categories, flag=True)
            message = "Like Done"
        else:
            return Response({'error': "Action Undetected"}, status=status.HTTP_400_BAD_REQUEST)

        count = item.number_of_likes

        return Response({'success': message, 'like_count': count}, status=status.HTTP_200_OK)


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
        ser_data = ChannelSerializer(flatList, many=True, context={"request": request})

        return Response(ser_data.data, status=status.HTTP_200_OK)


class CreateCommentView(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        content = request.data.get("content")
        channel_id = request.data.get("channel_id")
        item_id = request.data.get("item_id")
        create_comment.delay(content, channel_id, item_id, request.user.id)
        return Response({'success': "comment will be submitted"}, status=status.HTTP_200_OK)
