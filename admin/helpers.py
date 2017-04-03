from flask import session, request, g
from flask_login import current_user
import uuid
import json
import re


def generate_csrf_token(k):
    csrf_token = str(uuid.uuid4())
    session[k] = csrf_token
    # print "# %s" % csrf_token
    return csrf_token


def check_csrf_token(data, k):
    csrf_token = session.pop(k, None)
    # print csrf_token
    # print data.get("_csrf")
    return csrf_token and data.get("_csrf") == csrf_token


def setup_pagination(collection, page_max):
    after = request.args.get("after")
    before = request.args.get("before")
    start = after or before
    direction = (after and "forward") or (before and "backward")
    count, elements = g.db.find_all(collection, start, direction, page_max)
    last_page = count <= page_max and not before
    first_page = not start or (before and count <= page_max)
    direction == "backward" and elements.reverse()
    return elements, first_page, last_page


#email_validator = re.compile(r'^.+@[^.].*\.[a-z]{2,10}$')