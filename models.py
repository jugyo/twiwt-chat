# The Python Datastore API: http://code.google.com/appengine/docs/python/datastore/

from google.appengine.ext import db
from hashlib import sha1
from time import time
import datetime
import config


class Chat(db.Model):
    name = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now=True)


class Shout(db.Model):
    chat_name = db.StringProperty()
    user_name = db.StringProperty()
    text = db.TextProperty()
    created_at = db.DateTimeProperty(auto_now=True)

    def to_dict(self):
        return {'user_name': self.user_name,
            'text': self.text,
            'created_at': str(self.created_at),
            'chat_name': self.chat_name}

class User(db.Model):
    name                        = db.StringProperty()
    twitter_id                  = db.IntegerProperty()
    oauth_token                 = db.StringProperty()
    oauth_secret                = db.StringProperty()
    remember_token              = db.StringProperty()
    remember_token_expires_at   = db.DateTimeProperty()
    recent_chats                = db.StringListProperty()
    created_at                  = db.DateTimeProperty(auto_now=True)

    def update_remember_token(self):
        token = self.name + '-' + sha1('%s%s%s' % (self.name, config.session_secret_key, time())).hexdigest()
        self.remember_token = token
        expires_at = datetime.datetime.now() + datetime.timedelta(days=config.token_term)
        self.remember_token_expires_at = expires_at

    def delete_remember_token(self):
        self.remember_token = None
        self.remember_token_expires_at = None
