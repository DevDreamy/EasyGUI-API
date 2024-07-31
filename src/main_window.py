import json
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QComboBox,
    QFormLayout,
    QSpacerItem,
    QSizePolicy
)
from PyQt6.QtCore import Qt
from .flask_thread import FlaskThread
from .ui_elements.json_input import JsonInput
from .ui_elements.port_input import PortInput
from .ui_elements.status_indicator import StatusIndicator
from .ui_elements.auth_info import AuthInfo

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.json_enabled = False
        self.flask_thread = FlaskThread()
        self.custom_json = ''
        self.auth_type = 'None'
        self.server_running = False

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Easy GUI API')
        self.resize(400, 600)

        self.layout = QVBoxLayout()

        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.url_label = QLabel()
        self.url_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.form_layout.addRow(self.url_label)

        spacer1 = QSpacerItem(0, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        spacer_layout1 = QVBoxLayout()
        spacer_layout1.addItem(spacer1)
        self.form_layout.addRow('', spacer_layout1)

        self.port_input = PortInput()
        self.port_input.textChanged.connect(self.update_url_label)
        self.form_layout.addRow('Port:', self.port_input)

        self.auth_option_label = QLabel('Authentication Type:')
        self.form_layout.addRow(self.auth_option_label)

        self.auth_option_combo = QComboBox()
        self.auth_option_combo.addItems(['None', 'Basic Auth', 'JWT Bearer Auth'])
        self.auth_option_combo.currentIndexChanged.connect(self.update_auth_fields)
        self.form_layout.addRow(self.auth_option_combo)

        self.auth_info = AuthInfo()
        self.form_layout.addRow(self.auth_info)

        spacer2 = QSpacerItem(0, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        spacer_layout2 = QVBoxLayout()
        spacer_layout2.addItem(spacer2)
        self.form_layout.addRow('', spacer_layout2)

        self.json_option_label = QLabel('Response JSON Option:')
        self.form_layout.addRow(self.json_option_label)

        self.json_option_combo = QComboBox()
        self.json_option_combo.addItems(['Use default JSON', 'Write your own JSON'])
        self.json_option_combo.currentIndexChanged.connect(self.update_json_fields)
        self.form_layout.addRow(self.json_option_combo)

        self.json_input = JsonInput()
        self.form_layout.addRow(self.json_input)

        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.button_layout)

        self.toggle_button = QPushButton('Start Server')
        self.toggle_button.setFixedSize(200, 40)
        self.toggle_button.setStyleSheet(
            "font-size: 16px; padding: 10px;"
        )
        self.toggle_button.clicked.connect(self.toggle_server)
        self.button_layout.addWidget(self.toggle_button)

        self.status_layout = QHBoxLayout()
        self.status_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addLayout(self.status_layout)

        self.status_indicator = StatusIndicator()
        self.status_layout.addWidget(self.status_indicator)

        self.setLayout(self.layout)

        self.update_json_fields()
        self.update_status_indicator()
        self.update_url_label()

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

    def update_auth_fields(self):
        self.auth_type = self.auth_option_combo.currentText()
        if self.auth_type == 'JWT Bearer Auth':
            self.auth_info.set_text(
                f'Login URL: http://localhost:{self.port_input.text() or "4000"}/login\n'
                f'Username: user\n'
                f'Password: password'
            )
        elif self.auth_type == 'Basic Auth':
            self.auth_info.set_text(
                f'Username: user\n'
                f'Password: password'
            )
        else:
            self.auth_info.clear()

    def update_url_label(self):
        port = self.port_input.text()
        if port and port.isdigit() and 1 <= int(port) <= 65535:
            self.url_label.setText(f'URL: http://localhost:{port}')
        else:
            self.url_label.setText('URL: http://localhost:4000')
        self.update_auth_fields()

    def update_status_indicator(self):
        if self.json_enabled:
            self.status_indicator.set_active()
        else:
            self.status_indicator.set_inactive()

    def toggle_server(self):
        if not self.json_enabled:
            try:
                if self.json_option_combo.currentText() == 'Write your own JSON':
                    self.custom_json = self.json_input.toPlainText()
                    json_data = json.loads(self.custom_json)
                else:
                    self.custom_json = json.dumps(
                        {'message': 'This is the default JSON response'},
                        indent=4,
                    )
                    json_data = json.loads(self.custom_json)

                port = (
                    int(self.port_input.text())
                    if self.port_input.text().isdigit()
                    else 4000
                )
                if not (1 <= port <= 65535):
                    QMessageBox.critical(
                        self, 'Error', 'Port must be between 1 and 65535!'
                    )
                    return

                self.flask_thread.update_json(json_data)
                self.flask_thread.update_port(port)
                self.flask_thread.update_auth(self.auth_type)
                self.flask_thread.start()
                self.update_url_label()
                self.toggle_button.setText('Stop Server')
                self.json_enabled = True
                self.server_running = True

                self.port_input.setDisabled(True)
                self.json_option_combo.setDisabled(True)
                self.auth_option_combo.setDisabled(True)

                self.update_status_indicator()
            except json.JSONDecodeError:
                QMessageBox.critical(self, 'Error', 'Invalid JSON format!')
        else:
            self.flask_thread.stop()
            self.flask_thread.wait()
            self.flask_thread = FlaskThread()
            self.toggle_button.setText('Start Server')
            self.json_enabled = False
            self.server_running = False

            self.port_input.setDisabled(False)
            self.json_option_combo.setDisabled(False)
            self.auth_option_combo.setDisabled(False)

            self.update_json_fields()
            self.update_auth_fields()
            self.update_status_indicator()