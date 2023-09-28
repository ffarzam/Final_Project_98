from rest_framework import serializers

from .mixins import BookmarkMixin, LikeMixin
from .models import Channel, Episode, News
from interactions.models import NewsRead, EpisodeTrace


class ChannelSerializer(BookmarkMixin, serializers.ModelSerializer):
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ["id", "title", "subtitle", "xml_link", "last_update", "description", "language", "image_file_url",
                  "author", "owner", "owner_email", "is_bookmarked"]


class NewsSerializer(BookmarkMixin, LikeMixin, serializers.ModelSerializer):
    is_bookmarked = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    liked_count = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = ["id", "title", "channel", "published_date", "link", "source", "image_file_url", "guid", "is_liked",
                  "is_bookmarked", "liked_count"]

        def get_is_read(self, obj):
            user = self.context['request'].user
            if user.is_authenticated:
                return NewsRead.objects.filter(user=user, news=obj).exists()

            return False


class EpisodeSerializer(BookmarkMixin, LikeMixin, serializers.ModelSerializer):
    is_bookmarked = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    liked_count = serializers.SerializerMethodField()
    seconds_listened = serializers.SerializerMethodField()

    class Meta:
        model = Episode
        fields = ["id", "title", "subtitle", "channel", "published_date", "description", "image_file_url", "guid",
                  "audio_file_url", "duration", "explicit", "is_liked", "is_bookmarked", "liked_count"]

    def get_seconds_listened(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            qs = EpisodeTrace.objects.filter(user=user, episode=obj)
            if qs.exists():
                return qs.get().seconds_listened
        return False
