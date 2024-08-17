import json
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QTextEdit,
    QLineEdit,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QIntValidator
from ..ui_elements import AuthInfo


class Form(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.layout = QFormLayout()

        self.port_label = QLabel(self.tr('Port:'))
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText(
            self.tr('Enter port (default is 4000)')
        )
        self.port_input.setValidator(QIntValidator(1, 65535))
        self.port_input.textChanged.connect(self.update_url_label)
        self.layout.addRow(self.port_label, self.port_input)

        self.auth_option_label = QLabel(self.tr('Authentication Type:'))
        self.layout.addRow(self.auth_option_label)

        self.auth_option_combo = QComboBox()
        self.auth_option_combo.addItems(
            [
                self.tr('None'),
                self.tr('Basic Auth'),
                self.tr('JWT Bearer Auth'),
                self.tr('OAuth2'),
                self.tr('API Key'),
                self.tr('Digest'),
            ]
        )
        self.auth_option_combo.currentIndexChanged.connect(
            self.main_window.update_auth_fields
        )
        self.layout.addRow(self.auth_option_combo)

        self.auth_info = AuthInfo()
        self.layout.addRow(self.auth_info)

        self.json_option_label = QLabel(self.tr('JSON Response:'))
        self.layout.addRow(self.json_option_label)

        self.json_option_default = QCheckBox(self.tr('Use default JSON'))
        self.json_option_custom = QCheckBox(self.tr('Write your own JSON'))
        self.json_option_default.setChecked(True)

        self.json_option_default.toggled.connect(self.handle_json_selection)
        self.json_option_custom.toggled.connect(self.handle_json_selection)

        json_layout = QVBoxLayout()
        json_layout.addWidget(self.json_option_default)
        json_layout.addWidget(self.json_option_custom)
        self.layout.addRow(json_layout)

        self.import_json_button = QPushButton(self.tr('Import JSON File'))
        self.import_json_button.setFixedSize(120, 26)
        self.import_json_button.clicked.connect(self.import_json)
        self.layout.addRow(self.import_json_button)

        self.json_input = QTextEdit()
        self.json_input.setPlaceholderText(self.tr('Enter JSON here...'))
        self.layout.addRow(self.json_input)

        self.setLayout(self.layout)

    def update_url_label(self):
        port = self.port_input.text()
        if port and port.isdigit() and 1 <= int(port) <= 65535:
            self.main_window.top_bar.url_label.setText(f'URL: http://localhost:{port}')
        else:
            self.main_window.top_bar.url_label.setText('URL: http://localhost:4000')
        self.main_window.update_auth_fields()

    def handle_json_selection(self):
        if (
            self.sender() == self.form.json_option_default
            and self.form.json_option_default.isChecked()
        ):
            self.form.json_option_custom.setChecked(False)
        elif (
            self.sender() == self.form.json_option_custom
            and self.form.json_option_custom.isChecked()
        ):
            self.form.json_option_default.setChecked(False)
        if (
            not self.form.json_option_default.isChecked()
            and not self.form.json_option_custom.isChecked()
        ):
            self.sender().setChecked(True)
        self.update_json_fields()

    def import_json(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import JSON File",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options,
        )
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    json_data = json.load(file)
                    formatted_json = json.dumps(json_data, indent=4)
                    self.json_input.setText(formatted_json)
                    self.custom_json = formatted_json
                    self.json_option_custom.setChecked(True)
                    self.json_option_default.setChecked(False)
            except (json.JSONDecodeError, IOError) as e:
                QMessageBox.critical(
                    self, 'Error', f'Failed to load JSON file: {str(e)}'
                )