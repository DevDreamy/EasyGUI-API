from .base_server import BaseServer
from flask import jsonify


class NoAuthServer(BaseServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            return jsonify(self.json_data)
