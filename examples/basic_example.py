from flask import Flask, render_template, request
from flask_websockets import WebSockets, ws

app = Flask(__name__)
sockets = WebSockets(app, patch_app_run=True)
# To match only the first matching handler (pattern handlers before
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


@app.route('/')
def index():
    """
    Renders the index page.
    """
    return render_template('index.html')


if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)
