from PyQt6.QtCore import QThread, pyqtSignal
from flask import Flask, jsonify, request, Response
from werkzeug.serving import make_server
import datetime
import jwt
from .config import (
    DEFAULT_PORT,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    DEFAULT_SECRET_KEY,
    DEFAULT_CLIENT_ID,
    DEFAULT_CLIENT_SECRET,
    GRANT_TYPE,
)


class BaseFlaskServer(QThread):
    finished = pyqtSignal()

    def __init__(self, port):
        super().__init__()
        self.json_data = {}
        self.port = port or DEFAULT_PORT
        self.auth_type = 'None'
        self.username = DEFAULT_USERNAME
        self.password = DEFAULT_PASSWORD
        self.secret_key = DEFAULT_SECRET_KEY
        self.client_id = DEFAULT_CLIENT_ID
        self.client_secret = DEFAULT_CLIENT_SECRET
        self.grant_type = GRANT_TYPE
        self._server = None
        self._app = Flask(__name__)

    def run(self):
        self._server = make_server('localhost', self.port, self._app)
        self._server.serve_forever()

    def stop(self):
        if self._server:
            self._server.shutdown()

    def update_json(self, new_json):
        self.json_data = new_json


class NoAuthServer(BaseFlaskServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            return jsonify(self.json_data)


class BasicAuthServer(BaseFlaskServer):
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


class JwtAuthServer(BaseFlaskServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                if not self.check_jwt(token):
                    return self.authenticate_jwt()
            else:
                return self.authenticate_jwt()
            return jsonify(self.json_data)

        @self._app.route('/token', methods=['POST'])
        def token():
            auth = request.authorization
            if (
                auth
                and auth.username == self.username
                and auth.password == self.password
            ):
                token = jwt.encode(
                    {
                        'user': auth.username,
                        'exp': datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=30),
                    },
                    self.secret_key,
                    algorithm="HS256",
                )
                return jsonify({'token': token})
            return Response(
                'Incorrect username or password.\n'
                'Expected: user | password\n'
                f'Received: {auth.username} | {auth.password}',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'},
            )

    def check_jwt(self, token):
        try:
            data = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return data['user'] == self.username
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def authenticate_jwt(self):
        return Response(
            'Token is missing or invalid!',
            401,
            {'WWW-Authenticate': 'Bearer realm="Login Required"'},
        )


class OAuth2Server(BaseFlaskServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/token', methods=['POST'])
        def token():
            client_id = request.form.get('client_id')
            client_secret = request.form.get('client_secret')
            grant_type = request.form.get('grant_type')

            if grant_type == GRANT_TYPE:
                if (
                    client_id == self.client_id
                    and client_secret == self.client_secret
                ):
                    token = jwt.encode(
                        {
                            'client_id': client_id,
                            'exp': datetime.datetime.utcnow()
                            + datetime.timedelta(minutes=30),
                        },
                        self.secret_key,
                        algorithm="HS256",
                    )
                    return jsonify({'access_token': token})
                return Response('Invalid client ID or secret.', 401)
            return Response('Unsupported grant type.', 400)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                if not self.check_oauth2(token):
                    return self.authenticate_oauth2()
            else:
                return self.authenticate_oauth2()
            return jsonify(self.json_data)

    def check_oauth2(self, token):
        try:
            data = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return data['client_id'] == self.client_id
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def authenticate_oauth2(self):
        return Response(
            'Token is missing or invalid!',
            401,
            {'WWW-Authenticate': 'Bearer realm="Login Required"'},
        )
