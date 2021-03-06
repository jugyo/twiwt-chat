# coding: utf-8

#
# Flask Documentation:      http://flask.pocoo.org/docs/
# Jinja2 Documentation:     http://jinja.pocoo.org/2/documentation/
# Werkzeug Documentation:   http://werkzeug.pocoo.org/documentation/
# The Python Datastore API: http://code.google.com/appengine/docs/python/datastore/
#

#
# Pusher イベント
# チャンネル　        | イベント
# chat          | created
# chat.key()    | shout

from flask import Flask, redirect, url_for, session, request, render_template,\
                    abort, flash, get_flashed_messages, g, Response
from flaskext.oauth import OAuth
from models import *
import pusherapp
import config
import re
from time import time
import datetime
from hashlib import sha1
import utils

app = Flask(__name__)
app.secret_key = config.session_secret_key

pusher = pusherapp.Pusher(app_id=config.app_id, key=config.key, secret=config.secret)

########################################################
# Before Reqest
########################################################

@app.before_request
def before_request():
    g.config = config

    g.user = None
    if 'remember_token' in session:
        user = User.all().filter('remember_token =', session['remember_token']).get()
        if user is not None:
            if user.remember_token_expires_at and user.remember_token_expires_at > datetime.datetime.now():
                g.user = user
                if user.remember_token_expires_at < datetime.datetime.now() + datetime.timedelta(days=1):
                    # update remember_token
                    user.update_remember_token()
                    session['remember_token'] = user.remember_token
                    db.put(user)
            else:
                user.delete_remember_token()
                db.put(user)

    g.twitter_api_key = config.consumer_key

########################################################
# OAuth
########################################################

oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url            = 'http://api.twitter.com/1/',
    request_token_url   = 'http://api.twitter.com/oauth/request_token',
    access_token_url    = 'http://api.twitter.com/oauth/access_token',
    authorize_url       = 'http://api.twitter.com/oauth/authenticate',
    consumer_key        = config.consumer_key,
    consumer_secret     = config.consumer_secret
)

@twitter.tokengetter
def get_twitter_token():
    user = g.user
    if user is not None:
        return user.oauth_token, user.oauth_secret
    return None

@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))


@app.route('/logout')
def logout():
    if g.user is not None:
        g.user.delete_remember_token()
        db.put(g.user)
        flash('You were signed out')
    return redirect(request.referrer or url_for('index'))


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    user = User.all().filter('twitter_id =', int(resp['user_id'])).get()

    if user is None:
        user = User(twitter_id = int(resp['user_id']),
                    name = resp['screen_name'],
                    oauth_token = resp['oauth_token'],
                    oauth_secret = resp['oauth_token_secret'],
                    date = datetime.datetime.now()
                    )
        user.update_remember_token()
        db.put(user)

    if user.remember_token is None:
        user.update_remember_token()
        db.put(user)

    session['remember_token'] = user.remember_token

    flash('You were signed in')
    return redirect(next_url)

########################################################
# Chat
########################################################

# chat list
@app.route('/')
def index():
    shouts = Shout.all().order('-created_at').fetch(20)
    return render_template('index.html', shouts=shouts)


# shout
@app.route('/<name>', methods=['POST'])
def shout(name):
    chat = Chat.all().filter('name =', name).get()
    shout = Shout(chat_name=chat.name, text=request.form['text'])
    if g.user is not None:
        shout.user_name = g.user.name
    else:
        shout.user_name = 'null'
    shout.save()
    pusher[chat.key()].trigger('shout', data=shout.to_dict())
    return ''

def gen_chat_name(command):
    if command == '.random':
        return utils.randstr(10)
    else:
        return command[1:-1]

# show
@app.route('/<name>', methods=['GET'])
def chat(name):
    if re.match('^\.', name):
        return redirect(url_for('chat', name=gen_chat_name(name)))

    if re.match('^[\.a-zA-Z0-9\-_]+$', name) is not None:

        chat = Chat.all().filter('name =', name).get()

        if chat is None:
            chat = Chat(name=name)
            chat.save()

        if g.user:
            try:
                g.user.recent_chats.remove(chat.name)
            except ValueError:
                pass
            g.user.recent_chats.insert(0, chat.name)
            del g.user.recent_chats[100:]
            g.user.save()

        shouts = Shout.all().filter('chat_name =', chat.name).order('-created_at').fetch(20)
        shouts = map((lambda x: x.to_dict()), shouts)
        shouts.reverse()

        return render_template('chat.html', chat=chat, shouts=shouts)
    else:
        flash(u'チャット名に使えるのは英数字と　- (ハイフン) _ (アンダースコア) だけです！')
        return redirect(url_for('index'))
