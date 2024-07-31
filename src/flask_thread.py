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
    DEFAULT_EXPIRATION_TIME,
    DEFAULT_API_KEY,
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
        self.expiration_time = DEFAULT_EXPIRATION_TIME
        self.api_key = DEFAULT_API_KEY
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

    def error_401(self, message):
        return Response(
            message,
            401,
            {'WWW-Authenticate': 'Bearer realm="Login Required"'},
        )


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
                if self.check_jwt(token):
                    return jsonify(self.json_data)
                else:
                    return self.error_401('Invalid or expired token.')
            return self.error_401('Token is missing.')

        @self._app.route('/token', methods=['POST'])
        def token():
            auth = request.authorization

            if (
                auth
                and auth.username == self.username
                and auth.password == self.password
            ):
                expiration_time = (
                    datetime.datetime.utcnow()
                    + datetime.timedelta(minutes=self.expiration_time)
                )
                token = jwt.encode(
                    {
                        'user': auth.username,
                        'exp': expiration_time,
                    },
                    self.secret_key,
                    algorithm="HS256",
                )
                expires_in = (
                    expiration_time - datetime.datetime.utcnow()
                ).total_seconds()
                return jsonify(
                    {
                        'access_token': token,
                        'token_type': 'bearer',
                        'expires_in': expires_in,
                    }
                )
            return Response(
                'Incorrect username or password.\n'
                'Expected: user | password\n'
                f'Received: {auth.username} | {auth.password}',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'},
            )

        @self._app.route('/refresh', methods=['POST'])
        def refresh():
            auth_header = request.headers.get('Authorization')

            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

                try:
                    data = jwt.decode(
                        token,
                        self.secret_key,
                        algorithms=["HS256"],
                        options={"verify_exp": False},
                    )
                    new_expiration_time = (
                        datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=self.expiration_time)
                    )
                    new_token = jwt.encode(
                        {
                            'user': data['user'],
                            'exp': new_expiration_time,
                        },
                        self.secret_key,
                        algorithm="HS256",
                    )
                    new_expires_in = (
                        new_expiration_time - datetime.datetime.utcnow()
                    ).total_seconds()
                    return jsonify(
                        {
                            'access_token': new_token,
                            'token_type': 'bearer',
                            'expires_in': new_expires_in,
                        }
                    )
                except jwt.ExpiredSignatureError:
                    return self.error_401('Token has expired.')
                except jwt.InvalidTokenError:
                    return self.error_401('Invalid token.')
            return self.error_401('Token is missing.')

    def check_jwt(self, token):
        try:
            data = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return data['user'] == self.username
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False


class OAuth2Server(BaseFlaskServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/token', methods=['POST'])
        def token():
            client_id = request.form.get('client_id')
            client_secret = request.form.get('client_secret')
            grant_type = request.form.get('grant_type')

            if grant_type == self.grant_type:
                if (
                    client_id == self.client_id
                    and client_secret == self.client_secret
                ):
                    expiration_time = (
                        datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=self.expiration_time)
                    )
                    token = jwt.encode(
                        {
                            'client_id': client_id,
                            'exp': expiration_time,
                        },
                        self.secret_key,
                        algorithm="HS256",
                    )
                    expires_in = (
                        expiration_time - datetime.datetime.utcnow()
                    ).total_seconds()
                    return jsonify(
                        {
                            'access_token': token,
                            'token_type': 'bearer',
                            'expires_in': expires_in,
                        }
                    )
                return Response('Invalid client ID or secret.', 401)
            return Response('Unsupported grant type.', 400)

        @self._app.route('/refresh', methods=['POST'])
        def refresh():
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:
                    data = jwt.decode(
                        token,
                        self.secret_key,
                        algorithms=["HS256"],
                        options={"verify_exp": False},
                    )
                    new_expiration_time = (
                        datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=self.expiration_time)
                    )
                    new_token = jwt.encode(
                        {
                            'client_id': data['client_id'],
                            'exp': new_expiration_time,
                        },
                        self.secret_key,
                        algorithm="HS256",
                    )
                    new_expires_in = (
                        new_expiration_time - datetime.datetime.utcnow()
                    ).total_seconds()
                    return jsonify(
                        {
                            'access_token': new_token,
                            'token_type': 'bearer',
                            'expires_in': new_expires_in,
                        }
                    )
                except jwt.ExpiredSignatureError:
                    return self.error_401('Token has expired.')
                except jwt.InvalidTokenError:
                    return self.error_401('Invalid token.')
            return self.error_401('Token is missing.')

    def check_oauth2(self, token):
        try:
            data = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return data['client_id'] == self.client_id
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False


class ApiKeyAuthServer(BaseFlaskServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            api_key_header = request.headers.get('X-API-KEY')
            if api_key_header == self.api_key:
                return jsonify(self.json_data)
            return self.error_401('Invalid or missing API key.')
