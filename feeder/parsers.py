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

    title = get_text_or_none(channel, "title")

    subtitle = get_text_or_none(channel, "itunes:subtitle", namespaces=namespaces)

    last_update = convert_str_to_date_time(get_text_or_none(channel, "pubDate"))

    description = get_text_or_none(channel, "description")

    language = get_text_or_none(channel, "language")

    image_file_url = get_url_or_none(channel, "itunes:image", lookup='href', namespaces=namespaces)
    if image_file_url is None:
        image_file_url = get_url_or_none(channel, "image/url")

    author = get_text_or_none(channel, "itunes:author", namespaces=namespaces)

    owner = get_text_or_none(channel, "itunes:owner/itunes:name", namespaces=namespaces)

    owner_email = get_text_or_none(channel, "itunes:owner/itunes:email", namespaces=namespaces)

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
        title = get_text_or_none(item, "title")

        subtitle = get_text_or_none(item, "subtitle")

        description = get_text_or_none(item, "description")

        published_date = convert_str_to_date_time(get_text_or_none(item, "pubDate"))

        guid = get_text_or_none(item, "guid")

        image_file_url = get_url_or_none(item, "itunes:image", lookup='href', namespaces=namespaces)

        audio_file_url = get_url_or_none(item, "enclosure", lookup="url")

        duration = get_text_or_none(item, "itunes:duration", namespaces=namespaces)

        explicit = get_text_or_none(item, "itunes:explicit", namespaces=namespaces)

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

        title = get_text_or_none(item, "title")

        link = get_text_or_none(item, "link")

        published_date = convert_str_to_date_time(get_text_or_none(item, "pubDate"))

        source = get_url_or_none(item, "source", lookup="url")

        guid = get_text_or_none(item, "guid")

        image_file_url = get_url_or_none(item, "media:content", lookup="url", namespaces=namespaces)

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


def channel_parser_mapper(arg):
    choice = {
        "channel_parser_one": channel_parser_one,

    }
    return choice[arg.lower()]


def items_parser_mapper(arg):
    choice = {
        "item_parser_one": item_parser_one,
        "item_parser_two": item_parser_two

    }
    return choice[arg.lower()]


def item_model_mapper(arg):
    choice = {
        "Episode": Episode,
        "News": News,
    }
    return choice[arg.capitalize()]


def get_text_or_none(parent, arg, namespaces=None):
    result = parent.find(arg, namespaces)
    if result is not None:
        result = result.text
    return result


def convert_str_to_date_time(arg):
    date_format = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    if arg is not None:
        for value in date_format:
            try:
                if arg[-1] == "Z":
                    arg = arg.replace("T", " ").replace("Z", "")

                arg = datetime.strptime(arg, value).replace(tzinfo=pytz.UTC)
            except:
                pass
    return arg


def get_url_or_none(parent, arg, lookup=None, namespaces=None):
    result = parent.find(arg, namespaces)
    if result is not None:
        result = result.attrib.get(lookup) or result.text
    return result
