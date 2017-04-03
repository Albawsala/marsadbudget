from database import db
from bson.objectid import ObjectId
from bson.dbref import DBRef
import re

iskey = re.compile(r"[a-z][a-z_]*$")
islabel = re.compile(r"\w[\w ]*$", re.LOCALE)
isoption = re.compile(r"^\w[\w ]*(,\w[\w ]*){0,2}$", re.LOCALE)

FIELD_TYPES = ["string", "numeric", "choice", "options", "boolean", "object", "reference", "file"]
STRING_TYPES = ["simple", "multiline", "formated", "email", "url", "list"]
NUMERIC_TYPES = ["integer", "float", "date", "time", "datetime"]
SETUP_TYPES = {
    "all":      ["multiple", "condition"],
    "string":   ["required", "featured", "multilang"],
    "numeric":  ["required", "featured"             ],
    "choice":   [            "featured", "multilang"],
    "options":  [                        "multilang"],
    "boolean":  [            "featured"             ],
    "object":   [                                   ],
    "reference":["required",                        ],
    "file":     ["required",                        ],
}
FIELD_KEYS = {
    "all":      ["_type", "_label", "_setup", "_condition"],
    "string":   ["_options"],
    "numeric":  ["_options"],
    "choice":   ["_options"],
    "options":  ["_options"],
    "boolean":  [ ],
    "object":   [ ],
    "reference":["_options"],
    "file":     [ ],
}

schema = None

def save_collection(collection):
    assert isinstance(collection, dict), "collection object type not valid"
    
    assert "_name" in collection, "collection name not valid (1)"
    assert iskey.match(collection["_name"]), "collection name not valid (2)"
    if db.collections.find_one({"_name": collection["_name"]}):
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
    db.collections.insert(collection)


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
    
    elif _type == "boolean" or _type == "file":
        pass
    
    assert len(field) == len(FIELD_KEYS['all']) + len(FIELD_KEYS[_type]), "%s: field conf not valid" % key


def check_object(key, obj, obj_len=5):
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
    db.collections.save(collection)



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
        check_object_ed(key, field, field_ed)
        return
    
    if _type in ["choice", "options"]:
        field['_options'] = check_options(key, field_ed)
    
    assert len(field) == len(FIELD_KEYS['all']) + len(FIELD_KEYS[_type]), "%s: field conf not valid" % key


def check_object_ed(key, obj, obj_ed, obj_len=5):
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
                return collection_exists(obj[key])
            if type == "label":
                return True
    return False



def walk(start, level):
    ptr = start
    cur = level
    while(cur):
        ptr = ptr[len(ptr)-1]
        cur -= 1
    return ptr



def remove_collection(collection):
    assert collection_exists(collection)
    db.drop_collection(collection)
    db.collections.remove({"_name": collection})
    db.users.update({},{"$pull":{"shortcuts": collection}});



def get_collection(collection):
    return \
        iskey.match(collection) and \
        db.collections.find_one({"_name": collection})



def collection_exists(collection):
    return \
        iskey.match(collection) and \
        db.collections.find_one({"_name": collection})



def get_schema(collection):
    assert iskey.match(collection), "collection name not valid"
    obj = db.collections.find_one({"_name": collection}, {"_id": 0, "_schema": 1})
    return obj["_schema"]



def get_field(collection, field, _type):
    col = get_collection(collection)
    assert col, "Collection not found"
    ptr = col["_schema"]
    for node in field.split('.'):
        assert iskey.match(node) and node in ptr, "wrong field"
        ptr = ptr[node]
    assert ptr["_type"] == _type, "wrong field type"
    return col, ptr



# def add_option(collection, field, data):
#     label = data["option"]
#     parent = data["parent"]
#     ptr = field["_options"]
#     for node in parent.split('.'):
#         for opt in ptr:
#             if opt[0] == node:
#                 ptr = opt
#                 break;
#     for opt in ptr:
#         assert opt[0] != label, "duplicate label"
#     ptr.append([label])
#     db.collections.save(collection)



def get_fields_paths(obj):
    paths = []
    for key in obj["_order"]:
        field = obj[key]
        if field["_type"] == "object":
            subpaths = get_fields_paths(field)
            for p in subpaths:
                paths.append(key +'.'+ p)
        else:
            paths.append(key)
    return paths



def get_featured_paths(obj):
    paths = []
    for key in obj["_order"]:
        field = obj[key]
        _label = field['_label']
        _type = field['_type']
        if "multiple" in field["_setup"]:
            continue
        if field["_type"] == "object":
            step = key, _label, _type, False
            subpaths = get_featured_paths(field)
            for p in subpaths:
                p.insert(0, step)
                paths.append(p)
        elif "featured" in field["_setup"]:
            step = key, _label, _type, True
            paths.append([step])
    return paths



def get_leaves(path, pos, node):
    key, _label, _type, leaf = path[pos]
    pos += 1
    if leaf:
        if key not in node:
            return None
        if isinstance(node[key] , basestring) or _type != "string":
            return node[key]
        else:
            return node[key]["fr"]
    return get_leaves(path, pos, node[key])



def extract_label(path):
    res = ""
    for k,label,t,l in path:
        res = res + "." + label
    return res[1:]



def get_featured(docs, collection):
    sch = get_schema(collection)
    paths = get_featured_paths(sch)
    labels = []
    for path in paths:
        labels.append(extract_label(path))
    featured = []
    for doc in docs:
        docrow = {'id':str(doc["_id"]), 'cells':[]}
        for path in paths:
            docrow['cells'].append(get_leaves(path, 0, doc))
        featured.append(docrow)
    return labels, featured



def get_reference_content(dbref):
    if not isinstance(dbref, DBRef):
        return None
    sch = get_schema(dbref.collection)
    paths = get_featured_paths(sch)
    doc = db[dbref.collection].find_one({'_id':ObjectId(dbref.id)})
    content = []
    labels = []
    for path in paths:
        labels.append(extract_label(path))
        content.append(get_leaves(path, 0, doc))
    return zip(labels, content)
