from werkzeug import import_string, cached_property
from flask import session, request
from finders import find_all
import uuid
import re

class LazyView(object):
    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name
    @cached_property
    def view(self):
        return import_string(self.import_name)
    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)

def generate_csrf_token():
    csrf_token = str(uuid.uuid4())
    # print "+++   %s" % csrf_token
    session["csrf_token"] = csrf_token
    return csrf_token

def check_json():
    return \
        request.headers['Content-Type'] in ['application/json; charset=UTF-8', 'application/json'] and \
        request.is_xhr and \
        request.json and \
        check_csrf_token(request.json)

def check_csrf_token(data):
    csrf_token = session.pop("csrf_token", None)
    # print "++++   %s" % csrf_token
    # print "+++++   %s" % data["_csrf"]
    return \
        csrf_token and \
        "_csrf" in data and \
        isinstance(data["_csrf"], basestring) and \
        data["_csrf"] == csrf_token

def setup_pagination(collection, page_max):
    after = request.args.get("after")
    before = request.args.get("before")
    start = after or before
    direction = (after and "forward") or (before and "backward")
    count, elements = find_all(collection, start, direction, page_max)
    last_page = count <= page_max and not before
    first_page = not start or (before and count <= page_max)
    direction == "backward" and elements.reverse()
    return elements, first_page, last_page

import urllib
import httplib
import sgmllib
from urlparse import urljoin
from HTMLParser import HTMLParser

def get_article_image(url):
    
    class ImageFinder(HTMLParser):
        
        def __init__(self):
            HTMLParser.__init__(self)
            self.art_image = None
        
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if not self.art_image and tag == 'meta':
                if 'property' in attrs and 'content' in attrs and \
                attrs['property'].lower() == 'og:image':
                    self.art_image = attrs['content']
    
    if not url.startswith('http://') or url.startswith('https://'):
        url = 'http://%s' % url
    
    try:
        site = urllib.urlopen(url)
        contents = site.read()
        parser = ImageFinder()
        parser.feed(contents)
        return parser.art_image
    
    except:
        return None

def get_favicon_url(url):
    """
    Get the favicon used for site at url.
    - First try parsing for a favicon link in the html head.
    - Then try just /favicon.ico.
    - If neither found, return None
    """
    class FaviconFinder(sgmllib.SGMLParser):
        """
        A Parser class for finding the favicon used (if specified).
        """
        def __init__(self, verbose=0):
            sgmllib.SGMLParser.__init__(self, verbose)
            self.favicon_url = None
        def start_link(self, attributes):
            attributes = dict(attributes)
            if not self.favicon_url:
                if 'rel' in attributes and 'icon' in attributes['rel']:
                    if 'href' in attributes:
                        self.favicon_url = urljoin(url, attributes['href'])
    # Try to parse html at url and get favicon
    if not url.startswith('http://') or url.startswith('https://'):
        url = 'http://%s' % url
    try:
        site = urllib.urlopen(url)
        contents = site.read()
        favicon_parser = FaviconFinder()
        favicon_parser.feed(contents)
    except:
        pass
    # Another try block in case the parser throws an exception
    # AFTER finding the appropriate url.
    try:
        if favicon_parser.favicon_url:
            return favicon_parser.favicon_url
        else:
            url = '/'.join(url.split('/',3)[2:])
            root_directory = url.split('/')[0]
            favicon = httplib.HTTPConnection(root_directory)
            favicon.request('GET','/favicon.ico')
            response = favicon.getresponse()
            if response.status == 200:
                return 'http://%s/favicon.ico' % root_directory
            favicon = httplib.HTTPConnection('www.' + root_directory)
            favicon.request('GET','/favicon.ico')
            response = favicon.getresponse()
            if response.status == 200:
                return 'http://%s/favicon.ico' % ('www.' + root_directory)
    except:
        pass
    return None

import re
email_validator = re.compile(r'^.+@[^.].*\.[a-z]{2,10}$')