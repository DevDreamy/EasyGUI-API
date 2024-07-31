from .base_server import BaseServer
from flask import request, Response, jsonify


class BasicAuthServer(BaseServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            auth = request.authorization

            if (
                auth
                and auth.username == self.username
                and auth.password == self.password
            ):
                return jsonify(self.json_data)

            return Response(
                'Incorrect username or password.\n'
                f'Expected: {self.username} | {self.password}\n'
                f'Received: {auth.username} | {auth.password}',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'},
            )
