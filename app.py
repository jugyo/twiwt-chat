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

from flask import Flask, url_for, render_template, request, redirect, g, flash
from models import *
import pusherapp
import config
import re

app = Flask(__name__)
app.secret_key = config.session_secret_key

pusher = pusherapp.Pusher(app_id=config.app_id, key=config.key, secret=config.secret)

@app.before_request
def before_request():
    g.config = config

##############
# Chat
##############

# chat list
@app.route('/')
def index():
    shouts = Shout.all().order('-created_at').fetch(100)
    return render_template('index.html', shouts=shouts)


# show
@app.route('/<name>', methods=['GET'])
def chat(name):
    if re.match('^[a-zA-Z0-9\-_]+$', name) is not None:
        chat = Chat.all().filter('name =', name).get()
        if chat is None:
            chat = Chat(name=name)
            chat.save()
        shouts = Shout.all().filter('chat_name =', chat.name).order('-created_at').fetch(20)
        return render_template('chat.html', chat=chat, shouts=shouts)
    else:
        flash(u'チャット名に使えるのは英数字と　- (ハイフン) _ (アンダースコア) だけです！')
        return redirect(url_for('index'))


# shout
@app.route('/<name>', methods=['POST'])
def shout(name):
    chat = Chat.all().filter('name =', name).get()
    shout = Shout(chat_name=chat.name, text=request.form['text'])
    shout.save()
    # app.logger.info(chat.key())
    pusher[chat.key()].trigger('shout', data={'text': shout.text})
    return ''


# test
@app.route('/test', methods=['GET'])
def test():
    for item in Chat.all().fetch(100):
        item.delete()
    for item in Shout.all().fetch(100):
        item.delete()
    return 'OK'
