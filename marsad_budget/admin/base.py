import sys
sys.path.append('/home/user0/www')

from bson.objectid import ObjectId, InvalidId
from bson.dbref import DBRef
from pymongo import MongoClient
from datetime import datetime
from urllib2 import urlopen
from marsad_budget import conf
from common import utils
import json
import codecs
import os
import re
import yaml
import math
import ezodf


cx = MongoClient(conf.DB_HOST, conf.DB_PORT)
db_budget = cx[conf.DB_NAME]

FILEROOT = '/home/user0/www/marsad_budget/admin'


def correct_collections_count():
    for col in db_budget['collections'].find():
        col['_count'] = int(db_budget[col['_name']].count())
        db_budget['collections'].save(col)


if __name__ == '__main__':
	correct_collections_count()