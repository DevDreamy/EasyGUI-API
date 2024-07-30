from PyQt6.QtCore import QThread, pyqtSignal
from flask import Flask, jsonify, request, Response
from werkzeug.serving import make_server
from werkzeug.security import check_password_hash, generate_password_hash


class FlaskThread(QThread):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.json_data = {}
        self.port = 4000
        self.auth_type = 'None'
        self.username = ''
        self.password = ''
        self._server = None
        self._app = Flask(__name__)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            if self.auth_type == 'Basic Auth':
                auth = request.authorization
                if not auth or not self.check_auth(
                    auth.username, auth.password
                ):
                    return self.authenticate()
            return jsonify(self.json_data)

    def run(self):
        self._server = make_server('localhost', self.port, self._app)
        self._server.serve_forever()

    def update_json(self, new_json):
        self.json_data = new_json

    def update_port(self, port):
        self.port = port

    def update_auth(self, auth_type, username='', password=''):
        self.auth_type = auth_type
        self.username = username
        self.password = generate_password_hash(password)

    def check_auth(self, username, password):
        """Check if a username/password combination is correct."""
        return username == self.username and check_password_hash(
            self.password, password
        )

    def authenticate(self):
        """Sends a 401 response that enables basic auth."""
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials',
            401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'},
        )

    def stop(self):
        if self._server:
            self._server.shutdown()
