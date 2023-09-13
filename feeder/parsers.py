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


