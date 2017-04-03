from flask import g, current_app
try:
    from flaskext.uploads import UploadSet, IMAGES, DOCUMENTS, ALL
except ImportError:
    from flask_uploads import UploadSet, IMAGES, DOCUMENTS, ALL
from bson.objectid import ObjectId
from PIL import Image
import os

uploaded_images = UploadSet('images', IMAGES)
uploaded_documents = UploadSet('documents', ALL)


def insert_file(meta, file, mce_image=False):
    obj = {
        'title': meta['title'],
        'type': meta['type'],
    }
    
    if meta["type"] == "DOC":
        obj['lang'] = meta['lang']
        filename = uploaded_documents.save(file, name=u''+file.filename.lower())
        filesize = os.path.getsize(uploaded_documents.path(filename))

    elif meta["type"] == "IMG":
        if meta["width"]:
            try:
                width = int(meta['width'])
                assert width < 1600, "width value too large"
                im = resize_image(file, width)
                target = current_app.config['UPLOADED_IMAGES_DEST']
                filename = uploaded_images.resolve_conflict(target, u''+file.filename.lower())
                dst = target +'/'+ filename
                im.save(dst)

            except ValueError as err:
                raise AssertionError(err)
        else:
            filename = uploaded_images.save(file, name=u''+file.filename.lower())
            dst = uploaded_images.path(filename)
        
        filesize = os.path.getsize(dst)

    obj['filename'] = filename
    obj['filesize'] = filesize

    _id = g.db.insert('files', obj)

    if mce_image:
        return uploaded_images.url(filename)
    else:
        return _id


def update_file(meta, obj):
    obj["title"] = meta['title']
    
    if obj['type'] == 'DOC':
        obj["lang"] = meta.get('lang')

    elif obj['type'] == 'IMG':
        if meta["width"]:
            try:
                width = int(meta['width'])
                assert width < 1600, "width value too large"
                filepath = uploaded_images.path(obj['filename'])
                im = resize_image(filepath, width)
                im.save(filepath)

            except ValueError as err:
                raise AssertionError(err)

    g.db.save('files', obj)


def remove_file(file_id):
    obj = g.db.find_one('files', {"_id": ObjectId(file_id)})
    
    file_path = obj['type'] == 'DOC' and uploaded_documents.path(obj['filename']) or uploaded_images.path(obj['filename'])
    if os.path.isfile(file_path):
        os.remove(file_path)
    
    g.db.remove('files', obj)


def find_files(field, query):
    return g.db.find('files', {field: {'$regex':query, '$options':'i'}}, sort=[("_id",-1)])


def resize_image(file, width):
    im = Image.open(file)
    w, h = im.size
    size = width, int(h * width / w)
    return im.resize(size, Image.ANTIALIAS)
