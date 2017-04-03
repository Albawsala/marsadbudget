# -*- coding: utf-8 -*-

from finders import find, find_one
from database import db
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.http import BatchHttpRequest
from apiclient.errors import HttpError
from apiclient.discovery import build
from datetime import datetime
from diff_match_patch import diff_match_patch

import os
import re
import json
import Image
import urllib
import httplib
import httplib2
import sgmllib
from urlparse import urljoin
from HTMLParser import HTMLParser, HTMLParseError


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


def get_favicon(document):
	document['favicon'] = get_favicon_url(document['url'])


def get_favicon_albawsala(document):
    document['favicon'] = get_favicon_url(document['url'])


def calendar_event(document):
	fd = open('/home/user0/www/common/168a04081364291b25d7ea16315547d0e2a5e8d2-privatekey.p12', 'rb')
	pk = fd.read()
	fd.close()
	credentials = SignedJwtAssertionCredentials('545644560932@developer.gserviceaccount.com', pk, 'https://www.googleapis.com/auth/calendar', client_id='714521070007.apps.googleusercontent.com')
	http = httplib2.Http()
	http = credentials.authorize(http)
	service = build('calendar', 'v3', http=http)

	doc_id = document['_meta'].get('event_id')

	if document['type'] == 'PLE':
		fake_end = document['date'].replace(hour=20, minute=0, second=0, microsecond=0)
		
		if doc_id:
			debut = document['partie'][0]['debut'] or document['partie'][0]['debut_prevu']
			start = datetime.combine(document['date'], debut.time())

			fin = document['partie'][-1]['fin'] or fake_end
			end = datetime.combine(document['date'], fin.time())
		
		else:
			start = datetime.combine(document['date'], document['partie'][0]['debut_prevu'].time())
			fin = document['partie'][0]['fin'] or fake_end
			end = datetime.combine(document['date'], fin.time())

		event = {
			'start': {'dateTime': start.isoformat() + '+01:00'},
			'end': {'dateTime': end.isoformat() + '+01:00'},
			'summary': u'Séance plénière - جلسة عامة',
			'description': u'\n'.join([act['fr'] + ' - ' + act['ar'] for act in document['activite']]),
		}
    
	elif document['type'] == 'COM':
		start = datetime.combine(document['date'], document['debut'].time())
		com = db.dereference(document['commission'])
		event = {
			'start': {'dateTime': start.isoformat() + '+01:00'},
			'end': {'dateTime': start.replace(hour=start.hour + 1).isoformat() + '+01:00'},
			'summary': u'%s - %s' % (com['nom']['fr'], com['nom']['ar']),
			'description': u'\n'.join([act['fr'] + ' - ' + act['ar'] for act in document['activite']]),
		}
	
	try:
		if doc_id:
			res = service.events().update(calendarId='p6ud2o5pfmh278pv04kcc550p0@group.calendar.google.com', eventId=doc_id, body=event).execute()
		else:
			res = service.events().insert(calendarId='p6ud2o5pfmh278pv04kcc550p0@group.calendar.google.com', body=event).execute()
			if res.get('status') == 'confirmed':
				document['_meta']['event_id'] = res['id']
	
	except HttpError as err:
		print err._get_reason()
		print err.resp


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


def pre_diff(text):
	return text \
	.replace('<span>','') \
	.replace('</span>','') \
	.replace('\n',' ') \
	.replace('<p>',' { ') \
	.replace('<p dir="RTL">', ' { ') \
	.replace('<p dir="rtl">', ' { ') \
	.replace('</p>',' } ') \
	.replace('&amp;', '&')


def post_diff(text):
	DEL, INS, P, part, result = False, False, False, text, ''

	while True:
		tag, before, after, length = '', '', '', 0
		m = re.search('[{}<]', part)
		if m:
			pos = m.start()
		else:
			result += part
			break

		if part[pos] in ['{', '}']:
			length = 1
			tag = part[pos]

		elif part[pos] == '<':
			for char in part[pos:]:
				tag += char
				length += 1
				if char == '>': break

		if tag == '{':
			if P and (DEL or INS):
				tag = ''
			else:
				P = True
				tag = '<p>'
				if INS: after = '<ins >'
				if DEL: after = '<del >'

		elif tag == '}':
			if not P:
				tag = ''
			else:
				P = False
				tag = '</p>'
				if INS: before = '</ins >'
				if DEL: before = '</del >'

		elif tag == '<ins>': INS = True
		elif tag == '</ins>': INS = False
		elif tag == '<del>': DEL = True
		elif tag == '</del>': DEL = False

		if length > 1 and not P: tag = ''

		old_part = part[:pos]
		part = part[pos+length:]
		result += old_part + before + tag + after

	return result


def generate_diff(document):
	if document['version'] == 'v2' and document.get('old_num') != '':
		old_doc = find_one('constitution', {'version': 'v1', 'num': document['old_num']})
		if not old_doc: return

		# diff fr
		d = diff_match_patch()
		text1 = pre_diff(old_doc['texte']['fr'])
		text2 = pre_diff(document['texte']['fr'])
		lineText1, lineText2, lineArray = d.diff_linesToWords(text1, text2)
		diffs_fr = d.diff_main(lineText1, lineText2)
		d.diff_charsToLines(diffs_fr, lineArray)
		d.diff_cleanupSemantic(diffs_fr)
		result_fr = post_diff(d.diff_prettyHtml(diffs_fr))

		# diff ar
		text1 = pre_diff(old_doc['texte']['ar'])
		text2 = pre_diff(document['texte']['ar'])
		lineText1, lineText2, lineArray = d.diff_linesToWords(text1, text2)
		diffs_ar = d.diff_main(lineText1, lineText2)
		d.diff_charsToLines(diffs_ar, lineArray)
		d.diff_cleanupSemantic(diffs_ar)
		result_ar = post_diff(d.diff_prettyHtml(diffs_ar))

		document['_meta']['diffs'] = {
			'fr': result_fr,
			'ar': result_ar,
		}

	document['_meta']['exercept'] = {
        'fr': strip_html(document['texte']['fr'])[:150] + '...',
        'ar': strip_html(document['texte']['ar'])[:150] + '...',
    }


def get_exercept(content ,chars):
	text = strip_html(content)
	return text[:chars] + text[chars:chars + text[chars:].find(' ')]


def post_chroniques(document):

    class ImageFinder(HTMLParser):

        def __init__(self):
            HTMLParser.__init__(self)
            self.image = None
        
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if not self.image and tag == 'img':
            	self.image = attrs.get('src')


	document['_meta']['exercept'] = {
        'fr': get_exercept(document['texte']['fr'], 200),
        'ar': get_exercept(document['texte']['ar'], 200),
    }
    
    try:
        parser = ImageFinder()
        parser.feed(document['texte']['fr'])
        if not parser.image:
        	parser.feed(document['texte']['ar'])

        if parser.image and parser.image.startswith('/uploads'):
        	base_path = '/home/user0/www'
        	width = 100
        	im = Image.open(base_path + parser.image)
        	w, h = im.size
    		size = width, int(h * width / w)
    		im_new = im.resize(size, Image.ANTIALIAS)
    		new_url = '/uploads/thumbnails/'+ os.path.basename(parser.image)
    		im_new.save(base_path + new_url, 'png')

        	document['_meta']['preview_image'] = new_url
    
    except:
        pass


callbacks = {
    'breves': get_favicon,
    'albawsala_presse': get_favicon_albawsala,
    'constitution': generate_diff,
    'chroniques': post_chroniques,
}