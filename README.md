Twiwt:Chat
======

[http://chat.twiwt.org/](http://chat.twiwt.org/)

Setup & Start Server
-----

### setup submodule

    % git submodule update --init

### modify config.py:

* set your Pusher app_id, key and secret
* set your consumer key and secret for Twitter OAuth

### start server

    % dev_appserver.py .

Deploy
-----

### modify app.yaml

* check your application id in app.yaml

### deploy

    % appcfg.py update .

Note on Patches/Pull Requests
----

* Fork the project.
* Make your feature addition or bug fix.
* Send me a pull request. Bonus points for topic branches.

Issues
------

[http://chat.twiwt.org/issues](http://chat.twiwt.org/issues)
