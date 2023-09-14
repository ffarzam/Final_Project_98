from rest_framework import serializers
from .models import Channel, Episode, News


class ChannelListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = "__all__"


