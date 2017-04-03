from database import db
from bson.objectid import ObjectId, InvalidId
from bson.dbref import DBRef
from collections import collection_exists
from callbacks import callbacks
from datetime import datetime, timedelta
from flask_login import current_user
import re
import iso8601

LANGUAGES = ["ar", "fr", "en"]
iskey = re.compile(r"[a-z][a-z_]*$")
islabel = re.compile(r"\w[\w ]*$", re.LOCALE)
isEmail = re.compile(r"^.+@[^.].*\.[a-z]{2,10}$", re.IGNORECASE)
isURL = re.compile(ur"^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$", re.IGNORECASE)


def find_documents(col, field_name, q):
    field = col["_schema"]
    
    path = field_name.split('.')
    for key in path:
        field = field[key]

    if "multilang" in field["_setup"]:
        field_name += '.fr'

    if "integer" in field["_options"]:
        try:
            query = int(q)
        except ValueError as err:
            raise AssertionError(err)
    elif field["_type"] == "boolean":
        query = q == "true"
    else:
        query = {'$regex':q}

    return list(db[col["_name"]].find({field_name:query}, sort=[("_id",-1)]))


def get_referenced_document(dbref):
    return isinstance(dbref, DBRef) and db.dereference(dbref) or None


def convert_to_numeric(value, _type):
    try:
        if   _type == "integer":
            return int(value)
        elif _type == "float":
            return float(value)
        elif _type == "date":
            return datetime.strptime(value, "%d/%m/%Y")
        elif _type == "time":
            return datetime.strptime(value, "%H:%M")
        elif _type == "datetime":
            if value.find(':') == -1: return datetime.strptime(value, "%d/%m/%Y")
            return datetime.strptime(value, "%d/%m/%Y %H:%M")
    except ValueError:
        return None


def convert_to_reference(doc_id, collection):
    try:
        _id = ObjectId(doc_id)
    except InvalidId as err:
        raise AssertionError(str(err))
    assert collection == "files" or collection_exists(collection), "%s, collection doesn't exist" % collection
    dbref = DBRef(collection, _id)
    assert db.dereference(dbref), "document not found"
    return dbref


def check_field(key, value, sch):
    _type = sch["_type"]
    _setup = sch["_setup"]
    
    if _type == "string":
        _subtype = sch["_options"]
        if  "multilang" in _setup:
            assert isinstance(value, dict), "%s: expecting unicode" % key
            for k in value:
                assert k in LANGUAGES, "%s, unsupported language" % key
                assert isinstance(value[k], basestring), "%s: expecting unicode" % key
        else:
            assert isinstance(value, basestring), "%s: expecting basestring" % key
            assert value == "" or \
                ( _subtype in ["simple", "multiline", "formated", "list"] ) or \
                ( _subtype == "url" and isURL.match(value) ) or \
                ( _subtype == "email" and isEmail.match(value) ), "%s: bad format" % key
    
    elif _type == "numeric":
        assert isinstance(value, basestring), "%s: expecting unicode" % key
        if value == "":
            assert "required" not in _setup, "%s: required field" % key
        else:
            value = convert_to_numeric(value, sch["_options"])
            assert value != None, "%s: bad format" % key

    elif _type == "reference":
        assert isinstance(value, basestring), "%s: expecting unicode" % key
        if value == "":
            assert "required" not in _setup, "%s: required field" % key
        else:
            value = convert_to_reference(value, sch["_options"])
            assert value, "%s: bad format" % key

    elif _type == "file":
        assert isinstance(value, basestring), "%s: expecting unicode" % key
        if value == "":
            assert "required" not in _setup, "%s: required field" % key
        else:
            value = convert_to_reference(value, "files")
            assert value, "%s: bad format" % key

    elif _type == "boolean":
        assert isinstance(value, bool), "%s: expecting boolean" % key

    elif _type == "choice":
        assert isinstance(value, basestring), "%s: expecting unicode" % key
        assert islabel.match(value), "%s: expecting label format" % key
        assert value in sch["_options"], "%s: choice ( %s ) not valid" % (key, value)

    elif _type == "options":
        assert isinstance(value, list), "%s: expecting list" % key
        for opt in value:
            assert isinstance(opt, basestring), "%s: bad value" % key

    elif _type == "object":
        check_object(key, value, sch)
    return value


def check_object(k, obj, sch):
    assert isinstance(obj, dict), "%s: expecting dict" % k
    assert len(obj) <= len(sch["_order"]), "document doesn't have expected field count"
    
    for key in obj:
        assert key in sch["_order"], "%s missing in document" % key
        if "multiple" in sch[key]["_setup"]:
            assert isinstance(obj[key], list), "%s: expecting multi-field" % key
            for i in range(len(obj[key])):
                obj[key][i] = check_field(key, obj[key][i], sch[key])
        else:
            obj[key] = check_field(key, obj[key], sch[key])


def validate(collection, document):
    check_object(collection['_name'], document, collection['_schema'])


def insert_document(collection, document, draft):
    validate(collection, document)
    collection_name = collection['_name']
    
    document['_meta'] = {
        'draft': draft,
        'author': current_user.get_id(),
        'mtime': datetime.now()
    }
    
    if collection_name in callbacks:
        callbacks[collection_name](document)

    db[collection_name].insert(document)
    db.collections.update({"_name": collection_name}, {"$inc": {"_count": 1}})


def remove_document(collection, doc_id):
    db[collection].remove({"_id": ObjectId(doc_id)})
    db.collections.update({"_name": collection}, {"$inc": {"_count": -1}})


def update_document(collection, document_old, document, draft, mtime):
    collection_name = collection['_name']
    cursor = db[collection_name]
    
    _id = document_old['_id']
    _mtime = iso8601.parse_date(mtime)
    
    validate(collection, document)

    document['_meta'] = document_old.pop('_meta')
    document['_meta']['draft'] = draft
    
    if collection_name in callbacks:
        callbacks[collection_name](document)
    
    #TODO lock sync this shit
    document['_meta']['mtime'] = datetime.now()

    done = cursor.find_and_modify(
        query = {'_id': _id, '_meta.mtime':_mtime},
        update = document
    )

    while not done:
        document_mod = cursor.find_one({'_id': _id})
        _mtime = document_mod['_meta']['mtime']
        document['_meta']['twin'] = document_mod
        document['_meta']['mtime'] = datetime.now()

        done = cursor.find_and_modify(
            query = {'_id': _id, '_meta.mtime':_mtime},
            update = document
        )


def touch_document(collection, doc_id):
    try:
        _id = ObjectId(doc_id)

        return db[collection].find_and_modify(
            query = {'_id':_id},
            update = {'$set': {'_meta.touch.%s' % current_user.get_id(): datetime.now()}}
        )

    except InvalidId:
        pass
