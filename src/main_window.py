import json
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QSpacerItem,
    QSizePolicy,
    QFileDialog,
    QTextEdit,
    QLineEdit,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QIcon
from .auth_servers import (
    BasicAuthServer,
    JwtAuthServer,
    NoAuthServer,
    OAuth2Server,
    ApiKeyAuthServer,
    DigestAuthServer,
)
from .ui_elements import AuthInfo, StatusIndicator
from .config import (
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    DEFAULT_JSON_RESPONSE,
    DEFAULT_CLIENT_ID,
    DEFAULT_CLIENT_SECRET,
    GRANT_TYPE,
    DEFAULT_API_KEY,
    DEFAULT_REALM,
    DIGEST_ALGORITHM,
    DIGEST_QOP,
)
from .resources.styles import DARK_THEME_QSS
from .utils import tr, brazil_flag, usa_flag, spain_flag


class MainWindow(QWidget):
    def __init__(self, app, translator):
        super().__init__()

        self.app = app
        self.translator = translator
        self.server_instance = None
        self.custom_json = ''
        self.auth_type = 'None'
        self.server_running = False

        self.initUI()

    def initUI(self):
        self.setWindowTitle('EasyGUI API v1.2.0')
        self.resize(400, 600)

        stylesheet = DARK_THEME_QSS
        self.setStyleSheet(stylesheet)

        self.layout = QVBoxLayout()

        # Top bar layout
        self.top_bar_layout = QHBoxLayout()
        self.url_label = QLabel()
        self.url_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.top_bar_layout.addWidget(self.url_label)

        self.language_selector = QComboBox()
        self.language_selector.addItem(QIcon(usa_flag), "English")
        self.language_selector.addItem(QIcon(brazil_flag), "Portuguese")
        self.language_selector.addItem(QIcon(spain_flag), "Spanish")
        self.language_selector.setFixedWidth(120)
        self.language_selector.currentIndexChanged.connect(self.change_language)
        self.top_bar_layout.addWidget(
            self.language_selector, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(self.top_bar_layout)

        # Form layout
        self.form_layout = QFormLayout()

        spacer1 = QSpacerItem(
            0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        spacer_layout1 = QVBoxLayout()
        spacer_layout1.addItem(spacer1)
        self.form_layout.addRow('', spacer_layout1)

        self.port_label = QLabel(self.tr('Port:'))
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText(
            self.tr('Enter port (default is 4000)')
        )
        self.port_input.setValidator(QIntValidator(1, 65535))
        self.port_input.textChanged.connect(self.update_url_label)
        self.form_layout.addRow(self.port_label, self.port_input)

        spacer2 = QSpacerItem(
            0, 5, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        spacer_layout2 = QVBoxLayout()
        spacer_layout2.addItem(spacer2)
        self.form_layout.addRow('', spacer_layout2)

        self.auth_option_label = QLabel(self.tr('Authentication Type:'))
        self.form_layout.addRow(self.auth_option_label)

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
            self.update_auth_fields
        )
        self.form_layout.addRow(self.auth_option_combo)

        self.auth_info = AuthInfo()
        self.form_layout.addRow(self.auth_info)

        self.json_option_label = QLabel(self.tr('JSON Response:'))
        self.form_layout.addRow(self.json_option_label)

        self.json_option_default = QCheckBox(self.tr('Use default JSON'))
        self.json_option_custom = QCheckBox(self.tr('Write your own JSON'))
        self.json_option_default.setChecked(True)

        self.json_option_default.toggled.connect(self.handle_json_selection)
        self.json_option_custom.toggled.connect(self.handle_json_selection)

        json_layout = QVBoxLayout()
        json_layout.addWidget(self.json_option_default)
        json_layout.addWidget(self.json_option_custom)
        self.form_layout.addRow(json_layout)

        self.import_json_button = QPushButton(self.tr('Import JSON File'))
        self.import_json_button.setFixedSize(120, 26)
        self.import_json_button.clicked.connect(self.import_json)
        self.form_layout.addRow(self.import_json_button)

        self.json_input = QTextEdit()
        self.json_input.setPlaceholderText(self.tr('Enter JSON here...'))
        self.form_layout.addRow(self.json_input)

        self.layout.addLayout(self.form_layout)

        # Server Button
        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.toggle_button = QPushButton(self.tr('Start Server'))
        self.toggle_button.setFixedSize(200, 40)
        self.toggle_button.setStyleSheet("font-size: 14px; padding: 8px;")
        self.toggle_button.clicked.connect(self.toggle_server)
        self.button_layout.addWidget(self.toggle_button)
        self.layout.addLayout(self.button_layout)

        # Bottom Bar
        self.bottom_bar_layout = QHBoxLayout()
        self.credits_label = QLabel(
            '<a'
            ' style="text-decoration:none;color:#555555;"'
            ' href="https://github.com/DevDreamy">DevDreamy'
            '</a>'
        )
        self.credits_label.setOpenExternalLinks(True)
        self.credits_label.setTextFormat(Qt.TextFormat.RichText)
        self.credits_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.bottom_bar_layout.addWidget(self.credits_label)
        self.layout.addLayout(self.bottom_bar_layout)

        self.status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        self.status_layout.addWidget(self.status_indicator)
        self.bottom_bar_layout.addLayout(self.status_layout)

        self.setLayout(self.layout)

        self.update_json_fields()
        self.update_status_indicator()
        self.update_url_label()

    def handle_json_selection(self):
        if (
            self.sender() == self.json_option_default
            and self.json_option_default.isChecked()
        ):
            self.json_option_custom.setChecked(False)
        elif (
            self.sender() == self.json_option_custom
            and self.json_option_custom.isChecked()
        ):
            self.json_option_default.setChecked(False)
        if (
            not self.json_option_default.isChecked()
            and not self.json_option_custom.isChecked()
        ):
            self.sender().setChecked(True)
        self.update_json_fields()

    def update_json_fields(self):
        if not self.server_running:
            if self.json_option_default.isChecked():
                self.json_input.setDisabled(True)
                self.json_input.setText(
                    json.dumps(
                        DEFAULT_JSON_RESPONSE,
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
                f'<b>Token URL:</b> '
                f'http://localhost:{self.port_input.text() or "4000"}/token [POST]<br>'
                f'<b>Username:</b> {DEFAULT_USERNAME}<br>'
                f'<b>Password:</b> {DEFAULT_PASSWORD}<br>'
            )
        elif self.auth_type == 'Basic Auth':
            self.auth_info.set_text(
                f'<b>Username:</b> {DEFAULT_USERNAME}<br>'
                f'<b>Password:</b> {DEFAULT_PASSWORD}<br>'
            )
        elif self.auth_type == 'OAuth2':
            self.auth_info.set_text(
                f'<b>Token URL:</b> '
                f'http://localhost:{self.port_input.text() or "4000"}/token [POST]<br>'
                f'<b>client_id:</b> {DEFAULT_CLIENT_ID}<br>'
                f'<b>client_secret:</b> {DEFAULT_CLIENT_SECRET}<br>'
                f'<b>grant_type:</b> {GRANT_TYPE}<br>'
            )
        elif self.auth_type == 'API Key':
            self.auth_info.set_text(f'<b>X-API-KEY:</b> {DEFAULT_API_KEY}<br>')
        elif self.auth_type == 'Digest':
            self.auth_info.set_text(
                f'<b>Username:</b> {DEFAULT_USERNAME}<br>'
                f'<b>Password:</b> {DEFAULT_PASSWORD}<br>'
                f'<b>Realm:</b> {DEFAULT_REALM}<br>'
                f'<b>Algorithm:</b> {DIGEST_ALGORITHM}<br>'
                f'<b>qop:</b> {DIGEST_QOP}<br>'
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
        if self.server_running:
            self.status_indicator.set_active()
            self.status_indicator.setText(self.tr('Active'))
        else:
            self.status_indicator.setText(self.tr('Inactive'))
            self.status_indicator.set_inactive()

    def toggle_server(self):
        if not self.server_running:
            try:
                if self.server_instance:
                    self.server_instance.stop()
                    self.server_instance = None

                if self.json_option_custom.isChecked():
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

                if self.auth_type == 'Basic Auth':
                    self.server_instance = BasicAuthServer(port=port)
                elif self.auth_type == 'JWT Bearer Auth':
                    self.server_instance = JwtAuthServer(port=port)
                elif self.auth_type == 'OAuth2':
                    self.server_instance = OAuth2Server(port=port)
                elif self.auth_type == 'API Key':
                    self.server_instance = ApiKeyAuthServer(port=port)
                elif self.auth_type == 'Digest':
                    self.server_instance = DigestAuthServer(port=port)
                else:
                    self.server_instance = NoAuthServer(port=port)

                self.server_instance.update_json(json_data)
                self.server_instance.start()
                self.update_url_label()
                self.toggle_button.setText(self.tr('Stop Server'))
                self.server_running = True

                self.port_input.setDisabled(True)
                self.json_option_default.setDisabled(True)
                self.json_option_custom.setDisabled(True)
                self.auth_option_combo.setDisabled(True)
                self.import_json_button.setDisabled(True)
                self.update_status_indicator()
            except json.JSONDecodeError:
                QMessageBox.critical(self, 'Error', 'Invalid JSON format!')
        else:
            if self.server_instance:
                self.server_instance.stop()
                self.server_instance.wait()
                self.server_instance = None

            self.toggle_button.setText(self.tr('Start Server'))
            self.server_running = False

            self.port_input.setDisabled(False)
            self.json_option_default.setDisabled(False)
            self.json_option_custom.setDisabled(False)
            self.auth_option_combo.setDisabled(False)
            self.import_json_button.setDisabled(False)

            self.update_json_fields()
            self.update_auth_fields()
            self.update_status_indicator()

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

    def change_language(self):
        current_language = self.language_selector.currentText()
        if current_language == 'English':
            self.translator.load("translations/en_US.qm")
            self.import_json_button.setFixedSize(120, 26)
        elif current_language == 'Portuguese':
            self.translator.load("translations/pt_BR.qm")
            self.import_json_button.setFixedSize(150, 26)
        elif current_language == 'Spanish':
            self.translator.load("translations/es_ES.qm")
            self.import_json_button.setFixedSize(150, 26)
        self.app.installTranslator(self.translator)
        self.retranslateUi()

    def retranslateUi(self):
        self.port_input.setPlaceholderText(
            self.tr('Enter port (default is 4000)')
        )
        self.auth_option_label.setText(self.tr('Authentication Type:'))
        self.json_option_label.setText(self.tr('JSON Response:'))
        self.json_option_default.setText(self.tr('Use default JSON'))
        self.json_option_custom.setText(self.tr('Write your own JSON'))
        self.import_json_button.setText(self.tr('Import JSON File'))
        self.json_input.setPlaceholderText(self.tr('Enter JSON here...'))
        self.port_label.setText(self.tr('Port:'))
        if self.server_running:
            self.status_indicator.setText(tr('Active'))
            self.toggle_button.setText(self.tr('Stop Server'))
        else:
            self.toggle_button.setText(self.tr('Start Server'))
            self.status_indicator.setText(tr('Inactive'))

        self.auth_option_combo.clear()
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
