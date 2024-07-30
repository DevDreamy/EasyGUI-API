import json
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QComboBox,
    QLineEdit,
)
from flask_thread import FlaskThread


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.json_enabled = False
        self.flask_thread = FlaskThread()
        self.custom_json = ''

        self.initUI()

    def initUI(self):
        self.setWindowTitle('JSON Server')
        self.resize(400, 400)

        self.layout = QVBoxLayout()

        self.url_label = QLabel('URL:')
        self.layout.addWidget(self.url_label)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText('Enter port (default is 4000)')
        self.layout.addWidget(self.port_input)

        self.json_option_label = QLabel('JSON Option:')
        self.layout.addWidget(self.json_option_label)

        self.json_option_combo = QComboBox()
        self.json_option_combo.addItems(
            ['Use default JSON', 'Write your own JSON']
        )
        self.json_option_combo.currentIndexChanged.connect(
            self.update_json_fields
        )
        self.layout.addWidget(self.json_option_combo)

        self.json_input = QTextEdit()
        self.json_input.setPlaceholderText('Enter JSON here...')
        self.layout.addWidget(self.json_input)

        self.toggle_button = QPushButton('Enable')
        self.toggle_button.clicked.connect(self.toggle_server)
        self.layout.addWidget(self.toggle_button)

        self.setLayout(self.layout)

        self.update_json_fields()

    def update_json_fields(self):
        if not self.json_enabled:
            json_option = self.json_option_combo.currentText()
            if json_option == 'Use default JSON':
                self.json_input.setDisabled(True)
                self.json_input.setText(
                    json.dumps(
                        {'message': 'This is the default JSON response'},
                        indent=4,
                    )
                )
            else:
                self.json_input.setDisabled(False)
                self.json_input.setText(self.custom_json)

    def toggle_server(self):
        if not self.json_enabled:
            try:
                if (
                    self.json_option_combo.currentText()
                    == 'Write your own JSON'
                ):
                    self.custom_json = self.json_input.toPlainText()
                    json_data = json.loads(self.custom_json)
                else:
                    self.custom_json = json.dumps(
                        {'message': 'This is the default JSON response'},
                        indent=4,
                    )
                    json_data = json.loads(self.custom_json)

                self.flask_thread.update_json(json_data)
                port = (
                    int(self.port_input.text())
                    if self.port_input.text().isdigit()
                    else 4000
                )
                self.flask_thread.update_port(port)
                self.flask_thread.start()
                self.url_label.setText(f'URL: http://localhost:{port}')
                self.toggle_button.setText('Disable')
                self.json_enabled = True

                self.port_input.setDisabled(True)
                self.json_option_combo.setDisabled(True)
            except json.JSONDecodeError:
                QMessageBox.critical(self, 'Error', 'Invalid JSON format!')
        else:
            self.flask_thread.stop()
            self.flask_thread.wait()
            self.flask_thread = FlaskThread()
            self.toggle_button.setText('Enable')
            self.json_enabled = False

            self.port_input.setDisabled(False)
            self.json_option_combo.setDisabled(False)

            self.update_json_fields()
