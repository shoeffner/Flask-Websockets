================
Flask-Websockets
================

Flask-Websockets_ is a `Flask extension`_ which enables Flask_-style use of gevent-websockets_.
Take a look at the Documentation_ if you intend to use it.

.. _Flask-Websockets: https://Flask-Websockets.readthedocs.io/en/latest/
.. _Documentation: https://Flask-Websockets.readthedocs.io/en/latest/
.. _Flask extension: https://flask.palletsprojects.com/en/1.1.x/extensiondev/
.. _Flask: https://flask.palletsprojects.com
.. _gevent-websockets: https://gitlab.com/noppo/gevent-websocket


.. code:: python

    from flask import Flask
    from flask_websockets import WebSockets

    app = Flask(__name__)
    sockets = WebSockets(app)

    @sockets.on_message
    def echo(message):
        return message

    if __name__ == '__main__':
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
        server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
        server.serve_forever()


Installation is currently only possible via source.

.. code:: bash

    pip install git+https://github.com/shoeffner/Flask-Websockets@master#egg=Flask-Websockets


Features
--------

Flask-Websockets resulted from the need of a *raw* implementation of websockets to communicate with a Unity-WebGL app.
There is a multitude of `Flask extensions for websockets`_, but most of them require some sort of manual ``while True``-loops to handle requests.
Flask-Websockets tries to follow Flask-patterns as close as possible, thus it has the following features:

- :data:`~flask_websockets.ws` allows access to the websocket connection of the current context. It works similar to Flask's :attr:`~flask.request`.
- :meth:`~flask_websockets.WebSockets.on_message` is a powerful decorator to filter messages or catch all. The return value of functions decorated with :meth:`~flask_websockets.WebSockets.on_message` is sent as a reply, similar to `View functions`_. Note that it has limitations, notably :func:`~flask.flash` and custom HTTP status codes do not work.

.. _Flask extensions for websockets: https://pypi.org/search/?q=Flask-Websockets
.. _View functions: https://flask.palletsprojects.com/en/1.1.x/tutorial/views/


Caveats & Issues
----------------

Flask-Websockets is a tool I built for a specific purpose (communication between two specific components), thus it is very limited. For instance, inspired by Flask-Sockets_, it does not work properly with the flask debug runner.
Thus, the recommended way to run it is as done above:

.. code:: python

    if __name__ == '__main__':
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
        server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
        server.serve_forever()

Flask-Websockets does not have the following typical Flask-capabilities other Frameworks provide:

- :ref:`Blueprints <flask:blueprints>`
- :ref:`Cookie/Session handling <flask:sessions>`

There is also a list of "known" issues, though not all are Flask-Websockets' fault:

- Logging is not properly supported (`gevent-websocket#16`_)
- Reloading is currently not supported, this is essentially the same as for Flask-Sockets `flask-sockets#48`_
- The websockets do not seem to work using ``wss://``, instead, ``ws://`` needs to be used.

.. _gevent-websocket#16: https://gitlab.com/noppo/gevent-websocket/-/issues/16
.. _flask-sockets#48: https://github.com/heroku-python/flask-sockets/issues/48


Examples
--------

While the obligatory *echo*-example is given above, here are a few more examples.
A fully integrated example can be found in the examples_ directory.

.. _examples: https://github.com/shoeffner/Flask-Websockets/tree/master/examples

All examples below assume the following boilerplate:

.. code:: python

    from flask import Flask
    from flask_websockets import WebSockets, ws

    app = Flask(__name__)
    sockets = WebSockets(app)

    # EXAMPLE CODES HERE

    if __name__ == '__main__':
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
        server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
        server.serve_forever()

The simple echo shown at the beginning is employing the most basic use case of the on_message decorator: handle each and every message.
If the method returns ``None`` (which it implicitly does anyways), nothing is done.
If it returns a ``str`` or a ``bytes`` object, it is send via the websocket.
If it returns something of another type, an error is raised.
Note that this *catch-all* method is always called, even if another functions handles the same message.
To restrict this behavior, setup the app as follows: ``WebSockets(app, match_one=True)``.

.. code:: python

    @sockets.on_message
    def on_message(message):
        # do something
        return 'some result'

.. code:: python

    @sockets.on_message
    def reply(message):
        # This raises an error
        # return {'message': message, 'reply': 'Reply!'}
        # Instead, use:
        from Flask import jsonify
        return jsonify({'message': message, 'reply': 'Reply!'})

For long running tasks, it is possible to send status updates using the global :data:`~flask_websockets.ws`.

.. code:: python

    @sockets.on_message
    def do_some_work(message):
        import time
        ws.send('Starting work')
        time.sleep(3)
        ws.send('Hang in there')
        time.sleep(2)
        ws.send('Work done')


It is possible to use the :meth:`~flask_websockets.WebSockets.on_message` decorator to match (regex) patterns.
The patterns are compiled using the standard re_ module.

.. _re: https://docs.python.org/3/library/re.html

.. code:: python

    @sockets.on_message("^ECHO .*")
    def echo(message):
        _, msg = message.split(' ', 1)
        return msg

Similar to the :func:`flask.has_app_context` and :func:`flask.has_request_context`, Flask-Websockets comes with :func:`~flask_websockets.has_socket_context` to check whether a socket context is available.

.. code:: python

    from flask import render_template
    from flask_websockets import has_socket_context

    @sockets.one_message("^ECHO .*")
    def echo(message):
        print(has_socket_context())  # True
        return message

    @app.route('/')
    def index():
        print(has_socket_context())  # False
        return render_template('index.html')


Using :func:`~flask.url_for` in templates works with the special rule ``websocket`` and supplying ``_external=True, _scheme='ws'``.

.. code:: javascript

    ws = new WebSocket("{{ url_for('websocket', _external=True, _scheme='ws') }}");


Alternatives
------------

As mentioned above, there is a number of Flask extensions to enable websocket capabilites.
Here is a list of alternatives you should check out before using Flask-Websockets:

- Flask-Websocket_ (same name as this package without *s*) handles JSON messages to filter messages for ``.on(event)`` decorators
- Flask-SocketIO_ uses `socket.io`_ instead of gevent-websockets, and thus comes with rooms, filters, etc.
- Flask-Sockets_ heavily inspired the initial work for Flask-Websockets and offers cookie handling, routing, and Blueprint support; however it is less Flask-like and requires to pass a ``ws`` argument and implementing a custom loop.
- Flask-uWSGI-WebSocket_ uses a custom loop, but the repository seems to have moved (and I spent less than a minute to search for it).
- Flask-Socket-Tornado_ has Tornado-style sockets (I never used Tornado, so I have no clue what that means).

.. _Flask-Websocket: https://github.com/damonchen/flask-websocket/
.. _Flask-SocketIO: https://flask-socketio.readthedocs.io/en/latest/
.. _Flask-Sockets: https://github.com/heroku-python/flask-sockets
.. _Flask-uWSGI-WebSocket: https://pypi.org/project/Flask-uWSGI-WebSocket/
.. _socket.io: https://socket.io/
.. _Flask-Socket-Tornado: https://github.com/winkidney/flask-sockets-tornado


Important: not "approved"
-------------------------

This is *no* approved extension (and thus, I didn't put it up on PyPI):

    0. No: Maintainer (I probably don't have the resources nor need)
    1. Yes: Name is Flask-Websockets
    2. Yes: MIT license
    3. Yes: API characteristics
    4. Yes: I install it using ``pip install -e .``
    5. No: No test suite
    6. Yes: Documentation_.
    7. Yes: Supports >= 3.6

See also `Approved extensions`_.

.. _Documentation: https://Flask-Websockets.readthedocs.io/en/latest/
.. _Approved extensions: https://flask.palletsprojects.com/en/1.1.x/extensiondev/#approved-extensions
