# -*- coding: utf-8 -*-

import os, re, json
from bson.dbref import DBRef
from urllib import quote
from flaskext.babel import gettext, get_locale, format_datetime
from collections import get_reference_content, get_schema
from documents import get_referenced_document
from files import get_file, uploaded_images, uploaded_documents
from datetime import datetime

def get_reference_featured(ref):
    if isinstance(ref, DBRef):
        return get_reference_content(ref)

def to_json(obj, default={}):
    if obj: return json.dumps(obj)
    return default

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

def nl2br(value):
    #~ return u'\n\n'.join(u'%s' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(value))
    return value.replace('\n', '<br/>')
    
def get_file_url(file_id, thumb=None):
    obj = get_file(file_id)
    if not obj:
        return None
    
    filename = obj["filename"]
    
    if obj['type'] == 'IMG':
        if thumb:
            filename = os.path.splitext(filename)[0] + thumb
        return uploaded_images.url(filename)
    
    if obj['type'] == 'DOC':
        return uploaded_documents.url(filename)

def get_referenced(dbref):
    if dbref:
        return get_referenced_document(dbref)

def date_time_format(date_time, fmt="date"):
    if isinstance(date_time, basestring):
        return ""
    if fmt == "date":
        return date_time.strftime('%d/%m/%Y')
    if fmt == "date_full":
        return u'' + date_time.strftime(u'%A %d %B %Y').decode("utf-8")
    if fmt == "month_year":
        return u'' + date_time.strftime(u'%B %Y').decode("utf-8")
    if fmt == "datew":
        return format_datetime(date_time, 'dd MMMM yyyy')
    if fmt == "time":
        return date_time.strftime('%H:%M')
    if fmt == "datetime":
        return date_time.strftime('%a %d/%m/%Y - %H:%M')
    if fmt == "datetime_admin":
        return date_time.strftime('%d/%m/%Y %H:%M')

def parse_isodate(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

def get_option(opt, collection, path, lang=None):
    lang = lang or get_locale().language
    field = get_schema(collection)
    for step in path.split('.'):
        field = field[step]
    return field['_options'][opt][lang]

def set_lang_suffix(string):
    ln = get_locale().language
    if string and ln in string: return string[ln]

def get_choice_field(collection):
     return get_schema(collection)

def encode_url(url):
    return quote(url)

def get_lang():
    return get_locale().language

def get_dir(dir):
    lang = get_locale().language
    return {
        'fr': {'left':'left', 'right':'right'},
        'ar': {'left':'right', 'right':'left'}
    }[lang][dir]

def is_list(obj):
    return isinstance(obj, list)

def match_line(line, text):
    if not text: return False
    for l in text.split('\n'):
        if l == line: return True
    return False

def insert_quotes(text, quotes):
    r = re.compile('\[quote [rl]\]')
    conf = {
        'i': 0,
        'r': 'floati',
        'l': 'float'
    }
    
    def repl(m):
        if not len(quotes) > conf['i']: return ''
        quote = quotes[conf['i']]
        dep = get_referenced_document(quote['depute'])
        grp = get_referenced_document(dep['groupe'])
        conf['i'] += 1
        return '''
<blockquote class="%s">
    <span class="texte">%s</span>
    <a href="/depute/%s" class="float full top-10">
        <span class="clearfloat strong black">- %s</span>
        <span class="float left-5 grey">-- %s</span>
    </a>
</blockquote>''' % (
    conf[m.group(0)[7]],
    quote['texte']['fr'],
    dep['_id'],
    dep['prenom']['fr'] +' '+ dep['nom']['fr'],
    grp['abbr']['fr']
)

    return r.sub(repl, text)
