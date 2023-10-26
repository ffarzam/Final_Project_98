from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')

    def __str__(self):
        return f"{self.user} liked {self.content_object}"


class Comment(models.Model):
    content = models.TextField()
    comment_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def __str__(self):
        return f"{self.user} Commented on {self.content_object}"


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = _('Bookmark')
        verbose_name_plural = _('Bookmark')

    def __str__(self):
        return f"{self.user} Bookmarked on {self.content_object}"


class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey("feeder.Category", on_delete=models.CASCADE)
    # channel = models.ForeignKey("feeder.Channel", on_delete=models.CASCADE)
    count = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = _('Recommendation')
        verbose_name_plural = _('Recommendations')

    def __str__(self):
        return f"{self.user} liked {self.category} {self.count} times"


class EpisodeTrace(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    episode = models.ForeignKey("feeder.Episode", on_delete=models.CASCADE)
    seconds_listened = models.PositiveIntegerField()

    class Meta:
        verbose_name = _('Episode Trace')
        verbose_name_plural = _('Episodes Trace')

    def __str__(self):
        return f"{self.user} Listened {self.episode.title} {self.seconds_listened} Seconds"


class NewsRead(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    news = models.ForeignKey("feeder.News", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Read News')
        verbose_name_plural = _('Read News')

    def __str__(self):
        return f"{self.user} Read {self.news.title}"
