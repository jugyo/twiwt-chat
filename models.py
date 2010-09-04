# The Python Datastore API: http://code.google.com/appengine/docs/python/datastore/

from google.appengine.ext import db

class Chat(db.Model):
    name = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now=True)

class Shout(db.Model):
    chat_name = db.StringProperty()
    text = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now=True)
