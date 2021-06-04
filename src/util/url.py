import re

from lxml.html import parse
from urllib.request import urlopen

def url_valid(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None

def get_url_title(url):
    title = ""

    if url_valid(url):
        page = urlopen(url)
        p = parse(page)

        try:
            title = p.find(".//title").text 
        except:
            print("error getting title from url", url)
    else:
        # take the first 50 characters and call it the title
        title = url[:50]
        
    return title