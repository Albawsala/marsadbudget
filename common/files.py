from database import db
from bson.objectid import ObjectId
from flaskext.uploads import UploadSet, IMAGES, DOCUMENTS, ALL
import os

uploaded_images = UploadSet('images', IMAGES)
uploaded_documents = UploadSet('documents', ALL)


def insert_file(meta, files):
    assert "file" in files, "form not valid (1)"
    assert meta.get('title'), "form not valid (2)"
    assert "type" in meta, "form not valid (3)"
    assert meta["type"] in ["IMG", "DOC"], "file type not supported"
    
    obj = {
        'title': meta['title'],
        'type': meta['type'],
    }
    
    if meta["type"] == "DOC":
        assert "lang" in meta, "form not valid (4)"
        obj['lang'] = meta['lang']
        obj['scan'] = meta.get('scan')
        filename = uploaded_documents.save(files['file'])
        filesize = os.path.getsize(uploaded_documents.path(filename))

    elif meta["type"] == "IMG":
        filename = uploaded_images.save(files['file'])
        filesize = os.path.getsize(uploaded_images.path(filename))

    obj['filename'] = filename
    obj['filesize'] = filesize

    db['files'].insert(obj)


def update_file(meta, obj):
    assert meta.get('title'), "title required"
    obj["title"] = meta['title']
    
    if obj['type'] == 'DOC':
        obj["scan"] = meta.get('scan')
        obj["lang"] = meta.get('lang')

    db['files'].save(obj)


def remove_file(file_id):
    obj = db['files'].find_one({"_id": ObjectId(file_id)})
    file_path = obj['type'] == 'DOC' and uploaded_documents.path(obj['filename']) or uploaded_images.path(obj['filename'])
    if os.path.isfile(file_path): os.remove(file_path)
    db['files'].remove(obj)


def get_file(file_id):
    return db['files'].find_one({"_id": ObjectId(file_id)})


def find_files(form):
    assert "query" in form, "form not valid"
    assert "field" in form, "form not valid"
    assert form["field"] in ["title", "filename", "type"], "query not valid"
    return list(db['files'].find({form["field"]:{'$regex':form["query"]}}, sort=[("_id",-1)]))


def find_images():
    return db['files'].find({'type':'IMG'},sort=[('_id',-1)])
