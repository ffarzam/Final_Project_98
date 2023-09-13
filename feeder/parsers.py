from datetime import datetime
import pytz
import requests
from xml.etree import ElementTree as ET
from feeder.models import Episode, News


def get_info(xml_link):
    namespaces = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
                  "atom": "http://www.w3.org/2005/Atom",
                  "content": "http://purl.org/rss/1.0/modules/content/",
                  "media": "http://search.yahoo.com/mrss/"}
    response = requests.get(xml_link)
    root = ET.fromstring(response.content)
    channel = root.find("channel")
    return channel, namespaces


def channel_parser_one(xml_link):
    channel, namespaces = get_info(xml_link)

    title = channel.find("title").text if channel.find("title") is not None else None

    subtitle = channel.find("itunes:subtitle", namespaces=namespaces).text \
        if channel.find("itunes:subtitle", namespaces=namespaces) is not None \
        else None

    last_update = datetime.strptime(channel.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z") \
        if channel.find("pubDate") is not None \
        else None

    description = channel.find("description").text if channel.find("description") is not None else None

    language = channel.find("language").text if channel.find("language") is not None else None

    image_file_url = channel.find("itunes:image", namespaces=namespaces).attrib.get("href") \
        if channel.find("itunes:image", namespaces=namespaces) is not None \
        else None
    if image_file_url is None:
        image_file_url = channel.find("image/url").text \
            if channel.find("image/url") is not None \
            else None

    author = channel.find("itunes:author", namespaces=namespaces).text \
        if channel.find("itunes:author", namespaces=namespaces) is not None \
        else None

    owner = channel.find("itunes:owner/itunes:name", namespaces=namespaces).text \
        if channel.find("itunes:owner/itunes:name", namespaces=namespaces) is not None \
        else None

    owner_email = channel.find("itunes:owner/itunes:email", namespaces=namespaces).text \
        if channel.find("itunes:owner/itunes:email", namespaces=namespaces) is not None \
        else None

    channel_info = {
        "title": title,
        "subtitle": subtitle,
        "last_update": last_update,
        "description": description,
        "language": language,
        "author": author,
        "owner": owner,
        "owner_email": owner_email,
        "image_file_url": image_file_url,
    }

    return channel_info



