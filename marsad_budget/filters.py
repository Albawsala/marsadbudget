# -*- coding: utf-8 -*-
from flask import g
from bson.dbref import DBRef
import files
import os
import re

def set_lang_suffix(ml_string):
    return isinstance(ml_string, dict) and ml_string.get(g.lang_code) or ''

def remove_html(text):
    return re.sub('(<[^<]+?>)|(</[^<]+?>)', '', text)

def highlight(text , word , need_care = False):
    if need_care:
        text_p = text.replace(u"é","&eacute;")
        text_p = text_p.replace(u"à" , "&aacute;")
        text_p = text_p.replace(u"í" , "&iacute;")
        text_p = text_p.replace(u"â" , "&acirc;")
        text_p = text_p.replace(u"ê" , "&ecirc;")
        text_p = text_p.replace(u"è" , "&egrave;")
        text_p = text_p.replace(u"à" , "&agrave;")
    else:
        text_p = text
    kw = re.compile(word , re.IGNORECASE)
    return kw.sub('<span class="highlighted">%s</span>' % word,text_p)

def summerize(text):
    if text.__len__() > 1000:
        return text[:1000] + "..."
    return text

def get_file_url(obj, thumb=None):
    if isinstance(obj, DBRef):
        obj = g.db.dereference(obj)

    filename = obj["filename"]

    if obj['type'] == 'IMG':
        if thumb:
            filename = os.path.splitext(filename)[0] + thumb
        return files.uploaded_images.url(filename)

    if obj['type'] == 'DOC':
        return files.uploaded_documents.url(filename)
