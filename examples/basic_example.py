from uuid import uuid4

from flask import Flask, render_template, request, session
from flask_websockets import WebSockets, ws, has_socket_context

app = Flask(__name__)
app.secret_key = b'96iGXSNCLYfU5SCU6pzn2hH87gFF4PUrgxl7V5uKLLE'
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Strict'
)
sockets = WebSockets(app, patch_app_run=True)
# To match all only the first matching handler (pattern handlers before
# catch-all), supply match_one=True
# sockets = WebSockets(app, match_one=True, patch_app_run=True)


@sockets.on_message
def ping_pong(message):
    """
    Returns "Pong" if the message is "Ping".
    """
    if message == 'Ping':
        ws.send('Pong')


@sockets.on_message
def acknowledge(message):
    """
    Sends an ACK after each received message.
    """
    ws.send('ACK')


@sockets.on_message('^ECHO .*')
def echo(message):
    """
    Echos a message back to the client, splitting off
    a leading "ECHO ".
    """
    _, msg = message.split(' ', 1)
    return msg


@app.route('/broadcast', methods=['POST'])
def broadcast():
    """
    Broadcasts a message from a form field 'broadcast_form_message' to all
    available clients.
    """
    message = request.form['broadcast_form_message']
    return sockets.broadcast(message)


@app.route('/send', methods=['POST'])
def send():
    message = request.form['client_form_message']
    if has_socket_context():
        sockets.send(message)
    # Note that this is still an HTTP request, so we need a response
    return ''


@app.route('/')
def index():
    """
    Renders the index page.
    """
    # Set some session value to allow HTTP -> WebSocket for one client
    session['ws.ident'] = str(uuid4())
    return render_template('index.html')


if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)
