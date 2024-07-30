import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from flask import Flask, jsonify, request


class FlaskThread(QThread):
    def __init__(self):
        super().__init__()
        self.json_data = {}

    def run(self):
        app = Flask(__name__)

        @app.route('/', methods=['GET'])
        def jsonResponse():
            return jsonify(self.json_data)

        app.run(host='localhost', port=4000)

    def update_json(self, new_json):
        self.json_data = new_json


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.flask_thread = FlaskThread()
        self.json_enabled = False

    def initUI(self):
        self.setWindowTitle('JSON Server')

        self.layout = QVBoxLayout()

        self.url_label = QLabel('URL: localhost:4000')
        self.layout.addWidget(self.url_label)

        self.json_input = QTextEdit()
        self.json_input.setPlaceholderText('Enter JSON here...')
        self.layout.addWidget(self.json_input)

        self.toggle_button = QPushButton('Enable')
        self.toggle_button.clicked.connect(self.toggle_server)
        self.layout.addWidget(self.toggle_button)

        self.setLayout(self.layout)

    def toggle_server(self):
        if not self.json_enabled:
            try:
                json_data = json.loads(self.json_input.toPlainText())
                self.flask_thread.update_json(json_data)
                self.flask_thread.start()
                self.toggle_button.setText('Disable')
                self.json_enabled = True
            except json.JSONDecodeError:
                QMessageBox.critical(self, 'Error', 'Invalid JSON format!')
        else:
            self.flask_thread.terminate()
            self.flask_thread = FlaskThread()
            self.toggle_button.setText('Enable')
            self.json_enabled = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
