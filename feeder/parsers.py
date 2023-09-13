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


def item_parser_one(xml_link):
    channel, namespaces = get_info(xml_link)

    for item in channel.iter("item"):
        title = item.find("title").text if item.find("title") is not None else None

        subtitle = item.find("subtitle").text if item.find("subtitle") is not None else None

        description = item.find("description").text if item.find("description") is not None else None

        published_date = datetime.strptime(item.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z") \
            if item.find("pubDate") is not None \
            else None

        guid = item.find("guid").text if item.find("guid") is not None else None

        image_file_url = item.find("itunes:image", namespaces=namespaces).attrib.get("href") \
            if item.find("itunes:image", namespaces=namespaces) is not None \
            else None

        audio_file_url = item.find("enclosure").attrib.get("url") \
            if item.find("enclosure") is not None \
            else None

        duration = item.find("itunes:duration", namespaces=namespaces).text \
            if item.find("itunes:duration", namespaces=namespaces) is not None \
            else None

        explicit = item.find("itunes:explicit", namespaces=namespaces).text \
            if item.find("itunes:explicit", namespaces=namespaces) is not None \
            else None

        if audio_file_url is None or title is None or guid is None:
            continue

        item_info = {
            "title": title,
            "subtitle": subtitle,
            "published_date": published_date,
            "description": description,
            "guid": guid,
            "audio_file_url": audio_file_url,
            "duration": duration,
            "explicit": explicit,
            "image_file_url": image_file_url,
        }

        yield item_info


def item_parser_two(xml_link):
    channel, namespaces = get_info(xml_link)

    for item in channel.iter("item"):
        title = item.find("title").text if item.find("title") is not None else None

        link = item.find("link").text if item.find("link") is not None else None

        published_date = item_parser_two_string_to_date_time_convertor(item.find("pubDate").text) \
            if item.find("pubDate") is not None \
            else None

        source = item.find("source").attrib.get("url") if item.find("source") is not None else None

        guid = item.find("guid").text if item.find("guid") is not None else None

        image_file_url = item.find("media:content", namespaces=namespaces).attrib.get("url") \
            if item.find("media:content", namespaces=namespaces) is not None \
            else None

        if guid is None:
            continue

        item_info = {
            "title": title,
            "link": link,
            "published_date": published_date,
            "source": source,
            "guid": guid,
            "image_file_url": image_file_url,
        }

        yield item_info


def item_parser_two_string_to_date_time_convertor(pub_dat_str):
    pub_dat = pub_dat_str.replace("T", " ").replace("Z", "")
    pub_dat = datetime.strptime(pub_dat, "%Y-%m-%d %H:%M:%S")
    return pub_dat.replace(tzinfo=pytz.UTC)



