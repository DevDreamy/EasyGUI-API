from .base_server import BaseServer
from flask import request, jsonify


class ApiKeyAuthServer(BaseServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            api_key_header = request.headers.get('X-API-KEY')
            if api_key_header == self.api_key:
                return jsonify(self.json_data)
            return self.error_401('Invalid or missing API key.')
