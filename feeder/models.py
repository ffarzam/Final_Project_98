from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)


class Type(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class XmlLink(models.Model):
    xml_link = models.URLField(unique=True)
    channel_parser = models.CharField(max_length=50)
    items_parser = models.CharField(max_length=50)
    rss_type = models.ForeignKey(Type, on_delete=models.PROTECT, null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        try:
            name = Channel.objects.get(xml_link=self).title
            return f'{name} || {self.xml_link}'
        except:
            return f'{self.xml_link}'


class Channel(models.Model):
    title = models.CharField(max_length=50)
    subtitle = models.TextField(null=True, blank=True)
    xml_link = models.OneToOneField(XmlLink, on_delete=models.CASCADE)
    last_update = models.DateTimeField(null=True, blank=True)
    description = models.TextField()
    language = models.CharField(max_length=25)
    image_file_url = models.URLField(null=True, blank=True)
    author = models.TextField(null=True, blank=True)
    owner = models.CharField(max_length=250, null=True, blank=True)
    owner_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f'{self.title}'


class Episode(models.Model):
    title = models.CharField(max_length=250)
    subtitle = models.TextField(null=True, blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    description = models.TextField()
    published_date = models.DateTimeField()
    guid = models.TextField()
    audio_file_url = models.URLField()
    image_file_url = models.URLField(null=True, blank=True)
    duration = models.CharField(max_length=25, null=True, blank=True)
    explicit = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f'Podcast: {self.channel} || Episode: {self.title}'


