from __future__ import unicode_literals
from flask import g, redirect, url_for, flash
from flask_login import make_secure_token, current_user
import bcrypt


def admin_required(fn):
    def decorated_view(*args, **kwargs):
        if not current_user.data["role"] == "admin":
            flash("admin priviledge required")
            return redirect('/admin')
        return fn(*args, **kwargs)
    return decorated_view


def editor_required(fn):
    def decorated_view(*args, **kwargs):
        user_data = current_user.data
        if user_data["role"] == "admin":
            pass
        elif user_data["role"] != "editor":
            flash("editor priviledge required")
            return redirect('/admin')
        elif not user_data.get("limited"):
            pass
        elif 'collection' not in kwargs:
            pass
        elif kwargs['collection'] in user_data['collections']:
            pass
        else:
            flash("full editor priviledge required")
            return redirect('/admin')
        
        return fn(*args, **kwargs)
    return decorated_view


def add_shortcut(user, collection):
    if "shortcuts" not in user.data:
        user.data["shortcuts"] = [collection]
    elif collection not in user.data["shortcuts"]:
        user.data["shortcuts"].append(collection)
    else:
        return

    g.db.update('users', {"_id": user.data["_id"]}, {"$push": {"shortcuts": collection}})


def del_shortcut(user, collection):
    if "shortcuts" not in user.data:
        return

    if collection in user.data["shortcuts"]:
        user.data["shortcuts"].remove(collection)
        g.db.update('users', {"_id": user.data["_id"]}, {"$pull": {"shortcuts": collection}})


def get_user(email, password):
    data = g.db.find_one('users', {"email": email})
    if data is not None and \
    data["password"] == bcrypt.hashpw(password.encode('utf-8'), data["password"].encode('utf-8')):
        return User(data)

    return None


def get_user_by_id(user_id):
    data = g.db.find_one('users', {"_id": user_id})

    if data is not None:
        return User(data)

    return None


def get_user_by_token(token):
    data = g.db.find_one('users', {"token": token})

    if data is not None:
        return User(data)

    return None


def add_user(name, email, password):
    assert not g.db.find_one('users', {"email": email}), "email already in use"
    
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
    
    user = {
        "email": email,
        "name": name,
        "password": pw_hash,
        "role": "subscriber"
    }
    
    g.db.insert('users', user)


def update_profile(user, name, email, password):
    assert not g.db.find_one('users', {"_id": {"$ne": user['_id']}, "email": email}), "email already in use"
    
    if password:
        user["password"] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
    
    user['email'] = email
    user['name'] = name
    
    g.db.save('users', user)


def update_user(user, form):
    assert not g.db.find_one('users', {"_id": {"$ne": user['_id']}, "email": form['email']}), "email already in use"

    user['name'] = form['name']
    user['email'] = form['email']
    user['role'] = form['role']
    user['limited'] = form.get('limited')
    user['collections'] = map(lambda x:x.strip(), form['collections'].split('\n'))
    
    g.db.save('users', user)


class User:
    authenticated = True
    active = True
    anonymous = False
    
    def __init__(self, data):
        self.data = data
    
    def is_authenticated(self):
        return self.authenticated
    
    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return self.anonymous
    
    def get_id(self):
        return str(self.data["_id"])
    
    def get_auth_token(self):
        self.data["token"] = make_secure_token(self.data["password"])
        g.db.save('users', self.data)
        return self.data["token"]
