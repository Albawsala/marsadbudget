from flask import g
from bson.dbref import DBRef
from collections import get_featured as _get_featured
import files
import json
import os
import yaml


def yaml_dump(data):
    return yaml.safe_dump(data, default_flow_style=False)



def get_featured(obj):
    col = g.db.find_one('collections', {'_name': obj.collection})
    labels, getters = _get_featured(col)
    return zip(labels, getters)



def to_json(obj, default={}):
    return obj and json.dumps(obj) or default



def get_file_url(file_id, thumb=None):
    obj = g.db.find_one('files', {'_id':file_id})

    if not obj:
        return None
    
    filename = obj["filename"]
    
    if obj['type'] == 'IMG':
        if thumb:
            filename = os.path.splitext(filename)[0] + thumb
        return files.uploaded_images.url(filename)
    
    if obj['type'] == 'DOC':
        return files.uploaded_documents.url(filename)



def is_list(value):
    return isinstance(value, list)