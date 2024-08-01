from PyQt5.QtCore import QThread, pyqtSignal
from flask import Flask, Response
from werkzeug.serving import make_server
from ..config import (
    DEFAULT_PORT,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    DEFAULT_SECRET_KEY,
    DEFAULT_CLIENT_ID,
    DEFAULT_CLIENT_SECRET,
    GRANT_TYPE,
    DEFAULT_EXPIRATION_TIME,
    DEFAULT_API_KEY,
    DEFAULT_REALM,
    DIGEST_ALGORITHM,
    DIGEST_QOP,
)


class BaseServer(QThread):
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
        self.realm = DEFAULT_REALM
        self.digest_algorithm = DIGEST_ALGORITHM
        self.digest_qop = DIGEST_QOP
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
