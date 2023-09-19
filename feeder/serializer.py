from rest_framework import serializers


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = "feeder.Channel"
        fields = "__all__"


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = "feeder.News"
        fields = "__all__"


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = "feeder.Episode"
        fields = "__all__"
