import json
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QComboBox,
    QLineEdit,
)
from PyQt6.QtCore import Qt
from flask_thread import FlaskThread


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
        self.setWindowTitle('JSON Server')
        self.resize(400, 400)

        self.layout = QVBoxLayout()

        self.url_label = QLabel('URL:')
        self.layout.addWidget(self.url_label)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText('Enter port (default is 4000)')
        self.layout.addWidget(self.port_input)

        self.auth_option_label = QLabel('Authentication Type:')
        self.layout.addWidget(self.auth_option_label)

        self.auth_option_combo = QComboBox()
        self.auth_option_combo.addItems(['None', 'Basic Auth', 'JWT Bearer Auth'])
        self.auth_option_combo.currentIndexChanged.connect(self.update_auth_fields)
        self.layout.addWidget(self.auth_option_combo)

        self.auth_info_label = QLabel('')
        self.layout.addWidget(self.auth_info_label)

        self.json_option_label = QLabel('JSON Option:')
        self.layout.addWidget(self.json_option_label)

        self.json_option_combo = QComboBox()
        self.json_option_combo.addItems(['Use default JSON', 'Write your own JSON'])
        self.json_option_combo.currentIndexChanged.connect(self.update_json_fields)
        self.layout.addWidget(self.json_option_combo)

        self.json_input = QTextEdit()
        self.json_input.setPlaceholderText('Enter JSON here...')
        self.layout.addWidget(self.json_input)

        self.toggle_button = QPushButton('Enable')
        self.toggle_button.clicked.connect(self.toggle_server)
        self.layout.addWidget(self.toggle_button)

        self.status_layout = QHBoxLayout()
        self.status_layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )

        self.status_text = QLabel('Status:')
        self.status_layout.addWidget(self.status_text)

        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(80, 30)
        self.status_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_indicator.setStyleSheet(
            'border-radius: 15px; '
            'color: white; '
            'background-color: red; '
            'text-align: center; '
            'font-weight: bold; '
            'padding: 5px; '
        )
        self.status_layout.addWidget(self.status_indicator)

        self.layout.addLayout(self.status_layout)

        self.setLayout(self.layout)

        self.update_json_fields()
        self.update_status_indicator()

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
        if self.auth_type == 'JWT Auth':
            self.auth_info_label.setText(
                'Login URL: localhost:4000/login\nUsername: user\nPassword: password'
            )
        elif self.auth_type == 'Basic Auth':
            self.auth_info_label.setText('Username: user\nPassword: password')
        else:
            self.auth_info_label.setText('')

    def update_status_indicator(self):
        if self.json_enabled:
            self.status_indicator.setText('Active')
            self.status_indicator.setStyleSheet(
                'background-color: green; color: white; border-radius: 15px; padding: 3px; text-align: center; font-weight: bold;'
            )
        else:
            self.status_indicator.setText('Inactive')
            self.status_indicator.setStyleSheet(
                'background-color: red; color: white; border-radius: 15px; padding: 3px; text-align: center; font-weight: bold;'
            )

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

                self.flask_thread.update_json(json_data)
                self.flask_thread.update_port(
                    int(self.port_input.text())
                    if self.port_input.text().isdigit()
                    else 4000
                )
                self.flask_thread.update_auth(self.auth_type)
                self.flask_thread.start()
                self.url_label.setText(
                    f'URL: http://localhost:{self.flask_thread.port}'
                )
                self.toggle_button.setText('Disable')
                self.json_enabled = True
                self.server_running = True

                self.port_input.setDisabled(True)
                self.json_option_combo.setDisabled(True)
                self.auth_option_combo.setDisabled(True)

                self.update_auth_fields()
                self.update_status_indicator()
            except json.JSONDecodeError:
                QMessageBox.critical(self, 'Error', 'Invalid JSON format!')
        else:
            self.flask_thread.stop()
            self.flask_thread.wait()
            self.flask_thread = FlaskThread()
            self.toggle_button.setText('Enable')
            self.json_enabled = False
            self.server_running = False

            self.port_input.setDisabled(False)
            self.json_option_combo.setDisabled(False)
            self.auth_option_combo.setDisabled(False)

            self.update_json_fields()
            self.update_auth_fields()
            self.update_status_indicator()


import sys
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
