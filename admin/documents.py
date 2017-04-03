from flask import g, current_app
from bson.objectid import ObjectId, InvalidId
from bson.dbref import DBRef
from datetime import datetime, timedelta
from flask_login import current_user
import thread
import re
import iso8601
import yaml


LANGUAGES = ["ar", "fr", "en"]
iskey = re.compile(r"^[a-z_]+$")
islabel = re.compile(r"^\w[\w ]*$", re.LOCALE)
isEmail = re.compile(r"^.+@[^.].*\.[a-z]{2,10}$", re.IGNORECASE)
isURL = re.compile(ur"^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$", re.IGNORECASE)


def find_documents(col, query, path, field):
	f = schema = col["_schema"]
	col_name = col["_name"]
	
	path = path and path.split('.') or []
	for i,step in enumerate(path):
		f = f[step]
		if f["_type"] == "reference":
			ref_col_name = f["_options"]
			ref_col = g.db.find_one('collections', {'_name':ref_col_name})
			ref_path = '.'.join(path[i+1:])
			references = find_documents(ref_col, query, ref_path, field)
			if not references:
				return []
			
			field_name = '.'.join([step,'$id'])
			query = {'$in': references.distinct('_id')}
			return g.db.find(col_name, {field_name: query}, sort=[("_id",-1)])

	f = schema[field]

	if "multilang" in f["_setup"]:
		field += '.fr'

	if "integer" in f["_options"]:
		try:
			query = int(query)
		except ValueError as err:
			return []

	elif f["_type"] == "boolean":
		query = query == "true"
	
	else:
		query = {'$regex':query, '$options':'i'}

	field_name = '.'.join(path+[field])

	return g.db.find(col_name, {field_name: query}, sort=[("_id",-1)])


def convert_to_numeric(value, _type):
	try:
		if   _type == "integer":
			return int(value)
		elif _type == "float":
			return float(value)
		elif _type == "date":
			return datetime.strptime(value, "%d/%m/%Y")
		elif _type == "datetime":
			return datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
	except ValueError:
		return None


def convert_to_reference(doc_id, collection):
	assert isinstance(doc_id, basestring), "doc_id must be a string"
	try:
		_id = ObjectId(doc_id)
	except InvalidId:
		_id = doc_id

	assert collection == "files" or g.db.find_one('collections', {'_name':collection}), "%s, collection doesn't exist" % collection
	dbref = DBRef(collection, _id)
	assert g.db.dereference(dbref), "document not found"
	return dbref


def check_field(key, value, sch, root, path):
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
				( _subtype == "email" and isEmail.match(value) ), "%s: bad format1" % key
	
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

	elif _type == "yaml":
		root['_meta']['raw'][':'.join(path)] = value
		value = yaml.load(value)

	elif _type == "object":
		check_object(key, value, sch, root, path)
	
	return value


def check_object(k, obj, sch, root, path):
	assert isinstance(obj, dict), "%s: expecting dict" % k
	assert len(obj) <= len(sch["_order"]) + 1, "document doesn't have expected field count"

	for key in obj:
		if key == "_meta":
			continue
		assert key in sch["_order"], "%s missing in document" % key
		if "multiple" in sch[key]["_setup"]:
			assert isinstance(obj[key], list), "%s: expecting multi-field" % key
			for i in range(len(obj[key])):
				obj[key][i] = check_field(key, obj[key][i], sch[key], root, path+[key,str(i)])
		else:
			obj[key] = check_field(key, obj[key], sch[key], root, path+[key])


def validate(collection, document):
	check_object(collection['_name'], document, collection['_schema'], document, [])


def insert_document(collection, document, draft):
	document['_meta'] = {
		'draft': draft,
		'raw': {},
		'author': current_user.get_id(),
		'mtime': datetime.now()
	}

	validate(collection, document)
	collection_name = collection['_name']
	
	callbacks = current_app.config['CALLBACKS']
	if collection_name in callbacks['pre_save']:
		callbacks['pre_save'][collection_name](document)

	_id = g.db.insert(collection_name, document)
	g.db.update('collections', {"_name": collection_name}, {"$inc": {"_count": 1}})

	if collection_name in callbacks['post_save']:
		document['_id'] = _id
		callbacks['post_save'][collection_name](document)

	return _id


def remove_document(collection, document):
	callbacks = current_app.config['CALLBACKS']
	if collection in callbacks.get('pre_remove',{}):
		callbacks['pre_remove'][collection](document)
	g.db.remove(collection, {'_id': document['_id']})
	g.db.update('collections', {"_name": collection}, {"$inc": {"_count": -1}})


def update_document(collection, document_old, document, draft, mtime):
	collection_name = collection['_name']
	
	_id = document_old['_id']
	_mtime = iso8601.parse_date(mtime)
	
	document['_meta'] = document_old.pop('_meta')
	document['_meta']['draft'] = draft

	validate(collection, document)
	
	callbacks = current_app.config['CALLBACKS']
	if collection_name in callbacks['pre_save']:
		callbacks['pre_save'][collection_name](document, document_old)
	
	#TODO lock sync this
	document['_meta']['mtime'] = datetime.now()

	done = g.db.find_modify(
		collection_name,
		{'_id': _id, '_meta.mtime':_mtime},
		document
	)

	while not done:
		document_mod = g.db.find_one(collection_name, {'_id': _id})
		_mtime = document_mod['_meta']['mtime']
		document['_meta']['twin'] = document_mod
		document['_meta']['mtime'] = datetime.now()

		done = g.db.find_modify(
			collection_name,
			{'_id': _id, '_meta.mtime':_mtime},
			document
		)

	if collection_name in callbacks['post_save']:
		document['_id'] = _id
		callbacks['post_save'][collection_name](document)



def touch_document(collection, doc_id):
	try:
		_id = ObjectId(doc_id)
	except InvalidId:
		_id = doc_id

	return g.db.find_modify(
		collection,
		{'_id':_id},
		{'$set': {'_meta.touch.%s' % current_user.get_id(): datetime.now()}}
	)
