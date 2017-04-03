from flask import current_app
from email.mime.text import MIMEText
from HTMLParser import HTMLParser, HTMLParseError
from urlparse import urljoin
from PIL import Image
import smtplib
import os
import re
import urllib
import httplib
import sgmllib



class FaviconFinder(sgmllib.SGMLParser):
	
    def __init__(self, verbose=0):
        sgmllib.SGMLParser.__init__(self, verbose)
        self.favicon_url = None

    def start_link(self, attributes):
        attributes = dict(attributes)
        if not self.favicon_url:
            if 'rel' in attributes and 'icon' in attributes['rel']:
                if 'href' in attributes:
                    self.favicon_url = attributes['href']



def get_favicon_url(url):
    if not url.startswith('http://') or url.startswith('https://'):
        url = 'http://%s' % url

    try:
        site = urllib.urlopen(url)
        contents = site.read()
        favicon_parser = FaviconFinder()
        favicon_parser.feed(contents)
    except:
        pass
    
    try:
        if favicon_parser.favicon_url:
            return urljoin(url, favicon_parser.favicon_url)
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



def strip_html(text):
    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return u"" # ignore tags
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            import htmlentitydefs
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")

        return u'' + text # leave as is
    
    return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)



def get_exercept(content ,chars):
    text = strip_html(content)
    return text[:chars] + text[chars:chars + text[chars:].find(' ')]



def get_preview(document, field_name='texte'):
    if field_name not in document or not isinstance(document[field_name], dict):
        return
    
    langs = document[field_name].keys()
    exercept = {}

    for lang in langs:
        exercept[lang] = get_exercept(document[field_name][lang], 200)

    document['_meta']['exercept'] = exercept
    
    parser = ImageFinder()
    parser.feed(document[field_name][langs.pop()])
    while not parser.image and langs:
        parser.feed(document[field_name][langs.pop()])

    if parser.image and parser.image.startswith(current_app.config['UPLOADED_IMAGES_URL']):
        image_filename = parser.image[len(current_app.config['UPLOADED_IMAGES_URL']):]
        try:
            im = Image.open(current_app.config['UPLOADED_IMAGES_DEST'] + '/' + image_filename)
            w, h = im.size
            size = 100, 100
            if w > h:
                delta = (w - h)/2
                box = delta, 0, w-delta, h
            else:
                delta = (h - w)/2
                box = 0, delta, w, h-delta

            im_new = im.crop(box).resize(size, Image.ANTIALIAS)
            im_new.save(current_app.config['UPLOADED_THUMBNAILS_DEST'] + '/' + image_filename, 'png')
            new_url = current_app.config['UPLOADED_THUMBNAILS_URL'] + image_filename

            document['_meta']['preview_image'] = new_url
        except IOError:
            print "file not found"
        


class ImageFinder(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.image = None
    
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if not self.image and tag == 'img':
        	self.image = attrs.get('src')



def sendmail(message, sender, recipient, subject, replyto=None):
    errors, mailServer = None, None

    msg = MIMEText(message, 'plain', 'utf-8')

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    if replyto:
        msg['ReplyTo'] = replyto

    try:
        mailServer = smtplib.SMTP('localhost')
        mailServer.ehlo()
        mailServer.sendmail(sender, recipient, msg.as_string())
    except Exception as err:
        errors = err
    finally:
        if mailServer: mailServer.close()

    return errors
