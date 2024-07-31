from PyQt6.QtCore import QThread, pyqtSignal
from flask import Flask, jsonify, request, Response, make_response
from werkzeug.serving import make_server
import datetime
import jwt
from .config import DEFAULT_PORT, DEFAULT_USERNAME, DEFAULT_PASSWORD, DEFAULT_SECRET_KEY

class FlaskThread(QThread):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.json_data = {}
        self.port = DEFAULT_PORT
        self.auth_type = 'None'
        self.username = DEFAULT_USERNAME
        self.password = DEFAULT_PASSWORD
        self.secret_key = DEFAULT_SECRET_KEY
        self._server = None
        self._app = Flask(__name__)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            if self.auth_type == 'Basic Auth':
                auth = request.authorization
                if not auth or not self.check_auth(auth.username, auth.password):
                    return self.authenticate_basic()
            elif self.auth_type == 'JWT Auth':
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    if not self.check_jwt(token):
                        return self.authenticate_jwt()
                else:
                    return self.authenticate_jwt()
            return jsonify(self.json_data)

        @self._app.route('/login', methods=['POST'])
        def login():
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
            return make_response(
                'Incorrect username or password.\n'
                'Expected: user | password\n'
                f'Received: {auth.username} | {auth.password}',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'},
            )

    def run(self):
        self._server = make_server('localhost', self.port, self._app)
        self._server.serve_forever()

    def update_json(self, new_json):
        self.json_data = new_json

    def update_port(self, port):
        self.port = port

    def update_auth(self, auth_type):
        self.auth_type = auth_type

    def check_auth(self, username, password):
        return username == self.username and password == self.password

    def authenticate_basic(self):
        auth = request.authorization
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
        return make_response(
            'Token is missing or invalid!',
            401,
            {'WWW-Authenticate': 'Bearer realm="Login Required"'},
        )

    def stop(self):
        if self._server:
            self._server.shutdown()