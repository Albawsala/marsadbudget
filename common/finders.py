from flask import g
from bson.objectid import ObjectId, InvalidId
from bson.dbref import DBRef
from pymongo import MongoClient


class Finder():

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)


    def init_app(self, app, prefix='DB'):

        def key(suffix):
            return '%s_%s' % (prefix, suffix)

        host = app.config.get(key('HOST'), 'localhost')
        port = app.config.get(key('PORT'), 24107)
        name = app.config.get(key('NAME'), 'test')
        tz_aware = app.config.get(key('TZ_AWARE'), False)

        self.connection = MongoClient(host, port, tz_aware=tz_aware)
        self.db = self.connection[name]

        app.extensions['mongo'] = self

        @app.before_request
        def before_request():
            g.db = app.extensions['mongo']


    def find_all(self, collection, start, direction, limit, sort_by=('_id',-1)):
        query = {}
        cond = '$lt'
        sort_key, sort_dir = sort_by
        if start:
            obj = ObjectId(start)
            if direction == 'backward':
                cond = '$gt'
                sort_dir = sort_dir * -1
            query['_id'] = {cond: obj}
        result = self.db[collection].find(query, sort=[(sort_key,sort_dir)], limit=limit)
        return result.count(), list(result)


    def find(self, collection, query={}, limit=0, sort=[('_id',-1)], fields=None):
        query['_meta.draft'] = {'$ne':True}
        return self.db[collection].find(query, fields, sort=sort, limit=limit)


    def find_page(self, collection, query={}, limit=10, sort=[('_id',-1)], after=None, before=None):
        query['_meta.draft'] = {'$ne':True}
        
        if before:
            doc = g.db.find_one(collection, {'_id':before})
            query.setdefault('$or', [])
            last = {}
            for k,v in sort:
                if k not in doc: continue
                cond = {k: {'$lt': doc[k]}}
                cond.update(last)
                last[k] = doc[k]
                query['$or'].append(cond)
            elts = self.db[collection].find(query, sort=sort, limit=limit)
            count = elts.count()
            return {
                'liste': list(elts),
                'first_p': False,
                'last_p': count <= limit,
            }
        elif after:
            doc = g.db.find_one(collection, {'_id':after})
            query.setdefault('$or', [])
            last = {}
            for k,v in sort:
                if k not in doc: continue
                cond = {k: {'$gt': doc[k]}}
                cond.update(last)
                last[k] = doc[k]
                query['$or'].append(cond)
            elts = self.db[collection].find(query, sort=map(lambda x:(x[0],1), sort), limit=limit)
            count = elts.count()
            liste = list(elts)
            liste.reverse()
            return {
                'liste': liste,
                'first_p': count <= limit,
                'last_p': False,
            }
        else:
            elts = self.db[collection].find(query, sort=sort, limit=limit)
            count = elts.count()
            return {
                'liste': list(elts),
                'first_p': True,
                'last_p': count <= limit,
            }


    def find_one(self, collection, query):
        if isinstance(query.get('_id'), basestring):
    		try:
    			query['_id'] = ObjectId(query['_id'])
    		except InvalidId:
    			pass
        
        return self.db[collection].find_one(query)


    def find_distinct(self, collection, key):
        return sorted(self.db[collection].distinct(key))


    def dereference(self, obj):
        return isinstance(obj, DBRef) and self.db.dereference(obj) or None

    def update_article(self, collection, query, mod):
        if isinstance(query.get('_id'), basestring):
                try:
                        query['_id'] = ObjectId(query['_id'])
                except InvalidId:
                        pass
        return self.db[collection].update(query, mod)


class FinderModifier(Finder):

    def insert(self, collection, doc):
        return self.db[collection].insert(doc)


    def update(self, collection, query, mod):
        return self.db[collection].update(query, mod)


    def find_modify(self, collection, query, mod):
        return self.db[collection].find_and_modify(query, mod)


    def remove(self, collection, query):
        return self.db[collection].remove(query)


    def drop(self, collection):
        return self.db.drop_collection(collection)


    def save(self, collection, doc):
        return self.db[collection].save(doc)
