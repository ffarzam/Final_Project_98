from rest_framework import serializers
from .models import Channel, Episode, News


class ChannelListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = "__all__"


class NewsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"



