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


