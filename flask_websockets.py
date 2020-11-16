"""
Flask-Websockets is a Flask extension which enables Flask-style use of gevent-websockets.
"""
import re

from werkzeug.local import LocalStack
from werkzeug.local import LocalProxy
from werkzeug.routing import Rule

from geventwebsocket import WebSocketApplication


__version__ = '1.0.0'


def create_logger():
    """
    Creates a logger.
    The logger currently always uses the level :data:`~logging.DEBUG` and
    the :data:`flask.logging.default_handler`.
    """
    import logging
    from flask.logging import default_handler

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    log.addHandler(default_handler)
    return log


log = create_logger()
log.debug('Using Flask-Websockets version %s', __version__)

_cookie_sockets = dict()


def add_cookie_websocket(websocket):
    cookie = websocket.environ.get('HTTP_COOKIE')
    if cookie is not None:
        _cookie_sockets[cookie] = websocket


def remove_cookie_websocket(websocket):
    for cookie, socket in _cookie_sockets.items():
        if socket is websocket:
            break
    else:
        return
    _cookie_sockets.pop(cookie)


def get_websocket_by_cookie(environ):
    cookie = environ.get('HTTP_COOKIE')
    if cookie is not None:
        return _cookie_sockets.get(cookie, None)
    return None


class WebSockets:
    """
    """

    def __init__(self, app=None, match_one=False, patch_app_run=False):
        """
        The Flask-Websockets extension.
        """
        self.match_one = match_one
        self.patch_app_run = patch_app_run
        self.active_sockets = set()
        self._open_handler_registry = []
        self._pattern_handler_registry = []
        self._message_handler_registry = []
        self._close_handler_registry = []

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        """
        if self.patch_app_run:
            patch_app_run(app)
        app.url_map.add(Rule('/', endpoint='websocket', websocket=True))
        app.wsgi_app = WebSocketMiddleware(app.wsgi_app, self)

    def broadcast(self, message):
        """
        """
        log.debug('Broadcasting to %d clients', len(self.active_sockets))
        for socket in self.active_sockets:
            socket.send(message)
        return ''

    def on_open(self, fun):
        """
        """
        self._open_handler_registry.append(fun)
        return fun

    def on_message(self, fun_or_str, flags=0):
        """
        """
        if not isinstance(fun_or_str, str):
            self._message_handler_registry.append(fun_or_str)
            return fun_or_str

        def decorator(fun):
            fun._ws_pattern = re.compile(fun_or_str, flags)
            self._pattern_handler_registry.append(fun)
            return fun

        return decorator

    def on_close(self, fun):
        """
        """
        self._close_handler_registry.append(fun)
        return fun

    def _register_socket(self, websocket):
        self.active_sockets.add(websocket)

    def _unregister_socket(self, websocket):
        self.active_sockets.remove(websocket)

    def _handle_open(self, websocket, *args, **kwargs):
        log.debug('WebSocket client connected')
        for handler in self._open_handler_registry:
            handler(*args, **kwargs)
        self._register_socket(websocket)

    def _handle_message(self, websocket, message, *args, **kwargs):
        if message is None:
            log.debug('Empty WebSocket message received, ignoring.')
            return ''
        log.debug('WebSocket message received')

        handle_methods = [
            self._handle_pattern_messages,
            self._handle_catch_all_messages,
        ]
        for handle_method in handle_methods:
            matched_one = handle_method(websocket, message, *args, **kwargs)
            if matched_one:
                return ''
        return ''

    def _handle_pattern_messages(self, websocket, message, *args, **kwargs):
        for handler in self._pattern_handler_registry:
            if handler._ws_pattern.match(message) is None:
                continue
            response = handler(message, *args, **kwargs)
            self._send_response(websocket, response)
            if self.match_one:
                return True
        return False

    def _handle_catch_all_messages(self, websocket, message, *args, **kwargs):
        for handler in self._message_handler_registry:
            response = handler(message, *args, **kwargs)
            self._send_response(websocket, response)
            if self.match_one:
                return True
        return False

    def _handle_close(self, websocket, *args, **kwargs):
        log.debug('WebSocket client disconnected')
        for handler in self._close_handler_registry:
            handler(*args, **kwargs)
        self._unregister_socket(websocket)
        remove_cookie_websocket(websocket)

    def _send_response(self, websocket, response):
        if response is None:
            return
        websocket.send(response)


class WebSocketApp(WebSocketApplication):
    """
    """

    def __init__(self, websocket, sockets_manager):
        """
        """
        super().__init__(websocket)
        self.sockets_manager = sockets_manager

    def on_open(self, *args, **kwargs):
        self.sockets_manager._handle_open(self.ws, *args, **kwargs)

    def on_close(self, *args, **kwargs):
        self.sockets_manager._handle_close(self.ws, *args, **kwargs)

    def on_message(self, message, *args, **kwargs):
        self.sockets_manager._handle_message(self.ws, message, *args, **kwargs)


class WebSocketMiddleware:
    """
    """

    def __init__(self, wsgi_app, sockets_manager, socket_app=WebSocketApp):
        """
        """
        self.wsgi_app = wsgi_app
        self.sockets_manager = sockets_manager
        self.socket_app = socket_app

    def __call__(self, environ, start_response):
        """
        """
        if 'wsgi.websocket' not in environ:
            return self.handle_wsgi_app(environ, start_response)
        return self.handle_websocket(environ, start_response)

    def handle_websocket(self, environ, start_response):
        add_cookie_websocket(environ['wsgi.websocket'])
        socket_app = self.socket_app(environ['wsgi.websocket'], self.sockets_manager)
        with SocketContext(environ['wsgi.websocket']):
            with self.wsgi_app.__self__.request_context(environ):
                socket_app.handle()
        return []

    def handle_wsgi_app(self, environ, start_response):
        wsgi_websocket = get_websocket_by_cookie(environ)
        if wsgi_websocket is not None:
            with SocketContext(wsgi_websocket):
                return self.wsgi_app(environ, start_response)
        return self.wsgi_app(environ, start_response)


_socket_ctx_stack = LocalStack()
_socket_ctx_err_msg = """Working outside of websocket context.

This typically means that you attempted to use functionality that needed
to interface with the current websocket object in some way.

If you want to reply to an HTTP request using a websocket of the same client,
first make sure your websocket is connected.
You must also set a session cookie so that it is possible to identify the
client. In your first response set a session value such as:
    session['ws.ident'] = 'my_unique_identifier'
and consider the SameSite strategies and security considerations mentioned
here: https://flask.palletsprojects.com/en/1.1.x/security/#set-cookie-options

To check if you are in a proper websocket context (or a socket is connected
where you expect it to be), you can use flask_websockets.has_socket_context().
"""


def has_socket_context():
    """
    """
    return _socket_ctx_stack.top is not None


def _get_websocket():
    """
    """
    top = _socket_ctx_stack.top
    if top is None:
        raise RuntimeError(_socket_ctx_err_msg)
    return top.websocket


ws = LocalProxy(_get_websocket)


class SocketContext:
    """
    """

    def __init__(self, websocket):
        """
        """
        self.websocket = websocket

    def push(self):
        """
        """
        _socket_ctx_stack.push(self)

    def pop(self, exc=None):
        """
        """
        rv = _socket_ctx_stack.pop()
        assert rv is self, f"Popped wrong socket context.  ({rv!r} instead of {self!r})"

    def __exit__(self, exc_type, exc_value, tb):
        self.pop(exc_value)

    def __enter__(self):
        self.push()
        return self


def patch_app_run(app):
    """
    This patches :meth:`flask.Flask.run` to a version which does not directly fail using
    WebSockets, to quickly test out Flask-Websockets.
    It does not support all features of :meth:`flask.Flask.run` and is not
    recommended for production settings.

    For an alternative, please see :func:`~flask_websockets.run`, which is similar
    but without the debugging capabilites and no reloading.

    Thanks `@gmyers18`_, who provided the basic code here:
    https://github.com/heroku-python/flask-sockets/issues/48#issuecomment-301060798

    .. _`@gmyers18`: https://github.com/gmyers18
    """
    log.info('Patching app.run() to enable WebSockets.')

    def run(self, host=None, port=None, debug=None, **kwargs):
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler

        from werkzeug.serving import run_with_reloader
        from werkzeug.debug import DebuggedApplication

        from gevent import monkey
        monkey.patch_all()

        def run_server():
            if app.debug or debug:
                application = DebuggedApplication(app)
            else:
                application = app
            server = pywsgi.WSGIServer((host, port), application,
                                       handler_class=WebSocketHandler)
            server.serve_forever()

        run_with_reloader(run_server)
    run = run.__get__(app, app.__class__)
    setattr(app, 'run', run)


def run(app, host='', port=5000):
    """
    """
    log.info('Starting')
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer((host, port), app, handler_class=WebSocketHandler)
    server.serve_forever()
