from PyQt6.QtCore import QThread, pyqtSignal
from flask import Flask, jsonify
from werkzeug.serving import make_server


class FlaskThread(QThread):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.json_data = {}
        self.port = 4000
        self._server = None
        self._app = Flask(__name__)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            return jsonify(self.json_data)

    def run(self):
        self._server = make_server('localhost', self.port, self._app)
        self._server.serve_forever()

    def update_json(self, new_json):
        self.json_data = new_json

    def update_port(self, port):
        self.port = port

    def stop(self):
        if self._server:
            self._server.shutdown()
