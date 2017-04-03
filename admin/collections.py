# -*- coding: utf-8 -*-
from flask import g
from bson.objectid import ObjectId
from bson.dbref import DBRef
from datetime import datetime
import re

iskey = re.compile(r"^[a-z_0-9]+$")
islabel = re.compile(r"^\w[\w ]*$", re.LOCALE)
isoption = re.compile(r"^\w[\w ]*(,\w[\w ]*){0,2}$", re.LOCALE)

FIELD_TYPES = ["string", "numeric", "choice", "options", "boolean", "object", "reference", "file", "yaml"]
STRING_TYPES = ["simple", "multiline", "formated", "email", "url", "list"]
NUMERIC_TYPES = ["integer", "float", "date", "datetime"]
SETUP_TYPES = {
    "all":      ["multiple", "condition"],
    "string":   ["required", "featured", "multilang"],
    "numeric":  ["required", "featured"             ],
    "choice":   [            "featured", "multilang"],
    "options":  [                        "multilang"],
    "boolean":  [            "featured"             ],
    "object":   [                                   ],
    "reference":["required", "featured",            ],
    "file":     ["required",                        ],
    "yaml":     [                                   ],
}
FIELD_KEYS = {
    "all":      ["_type", "_label", "_setup", "_condition"],
    "string":   ["_options"],
    "numeric":  ["_options"],
    "choice":   ["_options"],
    "options":  ["_options"],
    "boolean":  [],
    "object":   ["_options"],
    "reference":["_options"],
    "file":     [],
    "yaml":     [],
}

schema = None



def save_collection(collection):
    assert isinstance(collection, dict), "collection object type not valid"
    
    assert "_name" in collection, "collection name not valid (1)"
    assert iskey.match(collection["_name"]), "collection name not valid (2)"
    if g.db.find_one('collections', {"_name": collection["_name"]}):
        raise Exception('Collection exists.')
    
    assert "_langs" in collection, "collection schema not found"
    assert isinstance(collection["_langs"], list), "collection langs attribute not valid"
    for ln in collection["_langs"]:
        assert isinstance(ln, basestring) and ln in ['fr', 'ar', 'en'], "collection langs data not valid"
    
    assert len(collection) == 3, "collection object not valid"
    
    assert "_schema" in collection, "collection schema not found"
    global schema
    schema = collection["_schema"]
    
    assert isinstance(schema, dict), "schema object not valid (1)" % key
    assert check(schema, "_label", "label"), "%s: field not valid (3)" % key
    check_object(collection["_name"], schema, 2)
    
    collection["_count"] = 0
    g.db.insert('collections', collection)



def check_conditions(key, field):
    conditions = {}
    
    for cond in field["_condition"]:
        assert isinstance(cond, basestring), "%s: condition not valid" % key
        k_v = cond.split(':')
        assert len(k_v) == 2, "%s: condition property not valid" % key
        k,v = k_v
        
        # check dotted field
        ptr = schema
        for node in k.split('.'):
            assert iskey.match(node) and node in ptr, "%s: wrong condition field" % key
            ptr = ptr[node]
        
        if v[0] == "[" and v[-1] == "]":
            v = v[1:-1].split(',')

        conditions[k] = v
    
    return conditions



def check_options(key, field):
    assert check(field, "_options", "list"), "%s: field options not valid" % key
    
    options = {}
    
    for opt in field["_options"]:
        assert isinstance(opt, basestring), "%s option not valid (1)" % key
        parts = opt.split(',')
        assert len(parts) in [2,3], "%s option not valid (2)" % key
        option = options[parts[0]] = {}
        option['fr'] = parts[1]
        if len(parts) == 3 and parts[2]:
            option['ar'] = parts[2]
    
    return options



def check_field(key, field):
    assert isinstance(field, dict), "%s: field not valid (1)" % key
    assert check(field, "_type", "type"), "%s: field not valid (2)" % key
    assert check(field, "_label", "label"), "%s: field not valid (3)" % key
    assert check(field, "_setup", "list"), "%s: field not valid (4)" % key
    assert check(field, "_condition", "list"), "%s: field not valid (5)" % key

    _type = field["_type"]
    
    for elt in field["_setup"]:
        assert elt in SETUP_TYPES[_type] or elt in SETUP_TYPES['all'], "%s field setup params not valid" % key
        
    field["_condition"] = check_conditions(key, field)
    
    if _type == "object":
        check_object(key, field)
        return
    
    if _type in ["choice", "options"]:
        field['_options'] = check_options(key, field)
    
    elif _type == "numeric":
        assert check(field, "_options", "numeric"), "%s: field subtype not valid" % key
    
    elif _type == "string":
        assert check(field, "_options", "string"), "%s: field subtype not valid" % key
    
    elif _type == "reference":
        assert check(field, "_options", "reference"), "%s: field subtype not valid" % key
    
    assert len(field) == len(FIELD_KEYS['all']) + len(FIELD_KEYS[_type]), "%s: field conf not valid" % key



def check_object(key, obj, obj_len=6):
    assert check(obj, "_order", "list"), "%s: object _order attribute not valid" % key
    _order = obj["_order"]
    assert len(_order) == len(obj) - obj_len, "%s: object elements count wrong" % key
    
    for k in _order:
        assert check(obj, k, "key"), "%s: %s field not valid" % (key, k)
        check_field(k, obj[k])



def update_collection(collection, data):
    assert isinstance(data, dict), "collection, object type not valid"
    assert "_schema" in data, "data not valid"
    assert len(data) == 1, "collection object not valid"
    
    global schema
    schema = data["_schema"]
    
    assert isinstance(schema, dict), "schema object not valid (1)" % key
    assert check(data["_schema"], "_label", "label"), "%s: field not valid (3)" % key
    collection["_schema"]["_label"] = data["_schema"]["_label"]
    check_object_ed(collection["_name"], collection["_schema"], data["_schema"], 2)
    g.db.save('collections', collection)



def check_field_ed(key, field, field_ed):
    assert isinstance(field_ed, dict), "%s: object type not valid" % key
    assert check(field_ed, "_type", "type"), "%s: field type not valid" % key
    assert check(field_ed, "_label", "label"), "%s: field label not valid" % key
    assert check(field_ed, "_setup", "list"), "%s: field setup not valid" % key
    assert check(field_ed, "_condition", "list"), "%s: field condition not valid" % key
    
    _type = field_ed["_type"]
    
    assert _type == field["_type"], "%s: field type mismatch" % key
    
    _setup = []
    
    if "featured" in field_ed["_setup"] and "featured" in SETUP_TYPES[_type]: _setup.append("featured")
    if "multiple" in field["_setup"]: _setup.append("multiple")
    if "multilang" in field["_setup"]: _setup.append("multilang")
    
    field["_setup"] = _setup
    field["_label"] = field_ed["_label"]
    field["_condition"] = check_conditions(key, field_ed)
    
    if _type == "object":
        field["_options"] = field_ed.get("_options", "")
        check_object_ed(key, field, field_ed)
        return
    
    if _type in ["choice", "options"]:
        field['_options'] = check_options(key, field_ed)
    
    assert len(field) == len(FIELD_KEYS['all']) + len(FIELD_KEYS[_type]), "%s: field conf not valid" % key



def check_object_ed(key, obj, obj_ed, obj_len=6):
    assert check(obj_ed, "_order", "list"), "%s: object _order attribute not valid" % key
    _order = obj_ed["_order"]
    assert len(_order) == len(obj_ed) - obj_len, "%s: object elements count wrong" % key
    
    cpt = 0
    for k in _order:
        assert check(obj_ed, k, "key"), "%s: %s field not valid" % (key, k)
        if "_old" in obj_ed[k]:
            del obj_ed[k]["_old"]
            assert k in obj["_order"], "%s: old field missing"
            check_field_ed(k, obj[k], obj_ed[k])
            cpt += 1
        else:
            check_field(k, obj_ed[k])
            obj[k] = obj_ed[k]
    
    # assert cpt == len(obj["_order"]), "%s: old data entries missing" % key
    obj["_order"] = _order



def check(obj, key, type):
    if key in obj:
        if type == "key":
            return isinstance(key, basestring) and iskey.match(key)
        if type == "list":
            return isinstance(obj[key], list)
        if isinstance(obj[key], basestring):
            if type == "type":
                return obj[key] in FIELD_TYPES
            if type == "string":
                return obj[key] in STRING_TYPES
            if type == "numeric":
                return obj[key] in NUMERIC_TYPES
            if type == "reference":
                return g.db.find_one('collections', {'_name': obj[key].split('.',1)[0]})
            if type == "label":
                return True
    return False



def remove_collection(collection):
    assert g.db.find_one('collections', {'_name': collection})
    g.db.drop(collection)
    g.db.remove('collections', {"_name": collection})
    g.db.update('users', {}, {"$pull":{"shortcuts": collection}});



def get_fields_paths(obj, stack=[]):
    paths = []

    for key in obj["_order"]:
        field = obj[key]
        _type = field["_type"]
        path = {
            'name': key,
            'type': _type,
        }
        
        if _type == "object":
            path['children'] = get_fields_paths(field, stack+[key])
        
        elif _type == "reference" and key not in stack:
            col = g.db.find_one('collections', {'_name': field['_options']})
            path['children'] = get_fields_paths(col['_schema'], stack+[key])
        
        paths.append(path)

    return paths



def get_featured(meta_data):
    labels = []
    getters = []

    for k in meta_data['_schema']['_order']:
        f = meta_data['_schema'][k]
        _setup = f['_setup']
        if 'featured' in f['_setup']:
            labels.append(f['_label'])
            getters.append(display_featured(k,f))

    return labels, getters



def display_featured(k,f):
    _type = f['_type']
    _setup = f['_setup']
    _options = f.get('_options')
    
    if _type == "numeric":
        if _options == "date":
            return lambda x: x and isinstance(x.get(k), datetime) and x[k].strftime('%d/%m/%Y') or ''
        if _options == "datetime":
            return lambda x: x and isinstance(x.get(k), datetime) and x[k].strftime('%d/%m/%Y %h:%M') or ''
        return lambda x: x and x.get(k) or ''
    
    if _type == "string":
        if "multilang" in _setup:
            return lambda x: x and isinstance(x.get(k), dict) and (x[k].get('fr') or x[k].get('ar')) or ''
        return lambda x: x and x.get(k) or ''
    
    if _type == "boolean":
        return lambda x: x and x.get(k) and u'✓' or ''

    if _type == "reference":
        getter = get_reference_featured(_options)
        return lambda x: x and isinstance(x.get(k), DBRef) and getter(g.db.dereference(x[k])) or ''

    return lambda x: x and x.get(k) or ''



def get_reference_featured(col_name):
    col = g.db.find_one('collections', {'_name': col_name})

    for k in col['_schema']['_order']:
        f = col['_schema'][k]
        if 'featured' in f['_setup']:
            return display_featured(k,f)
