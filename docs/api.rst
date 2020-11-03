API
===

.. module:: flask_websockets

WebSockets
----------

.. autoclass:: WebSockets
   :members:
   :inherited-members:


WebSocketApp
------------

.. autoclass:: WebSocketApp
   :members:
   :inherited-members:


WebSocketMiddleware
-------------------

.. autoclass:: WebSocketMiddleware
   :members:
   :inherited-members:


Application Globals
-------------------

.. data:: ws

    A namespace object that holds the currently active socket connection inside a :class:`SocketContext`.

    This is a :class:`werkzeug.local.LocalProxy`.


Useful Functions and Classes
----------------------------

.. autofunction:: has_socket_context

.. autoclass:: SocketContext
   :members:

.. autofunction:: patch_app_run

.. autofunction:: run
