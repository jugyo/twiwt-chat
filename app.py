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

from flask import Flask, url_for, render_template, request, redirect, g
from models import *
import pusherapp
import config

app = Flask(__name__)
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
    return render_template('index.html', chats=Chat.all().order('-created_at'))


# show
@app.route('/<name>', methods=['GET'])
def chat(name):
    chat = Chat.all().filter('name =', name).get()
    if chat is None:
        chat = Chat(name=name)
        chat.save()
    shouts = Shout.all().filter('chat =', chat).order('-created_at').fetch(20)
    return render_template('chat.html', chat=chat, shouts=shouts)


# shout
@app.route('/<name>', methods=['POST'])
def shout(name):
    chat = Chat.all().filter('name =', name).get()
    shout = Shout(chat=chat, text=request.form['text'])
    shout.save()
    # app.logger.info(chat.key())
    pusher[chat.key()].trigger('shout', data={'text': shout.text})
    return ''


# # create
# @app.route('/c', methods=['POST'])
# def create_chat():
#     # TODO: name のバリデーション
#     name = request.form['name']
#     chat = Chat.all().filter('name=', name).get()
#     app.logger.info(chat)
#     if chat is None:
#         chat = Chat(name=name)
#         chat.save()
#     return redirect(url_for('chat', name=chat.name))


# TODO: あとで消す
@app.route('/push')
def push():
    pusher['chat'].trigger('created', data={'name': 'foo'})
    return redirect(url_for('index'))


@app.route('/add', methods=["POST"])
def add():
    todo = Todo(text=request.form['text'])
    todo.save()
    return redirect(url_for('index'))
