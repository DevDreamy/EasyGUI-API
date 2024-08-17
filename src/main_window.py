import json
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer
from .auth_servers import (
    BasicAuthServer,
    JwtAuthServer,
    NoAuthServer,
    OAuth2Server,
    ApiKeyAuthServer,
    DigestAuthServer,
)
from .ui_elements import (
    TopBar,
    BottomBar,
    Form,
    ServerButton,
)
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
from .utils import tr


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
        self.top_bar = TopBar(self)
        self.layout.addWidget(self.top_bar)

        # Form layout
        self.form = Form(self)
        self.layout.addWidget(self.form)

        # Server Button
        self.server_button = ServerButton(self)
        self.layout.addWidget(self.server_button)

        # Bottom Bar
        self.bottom_bar = BottomBar(self)
        self.layout.addWidget(self.bottom_bar)

        self.setLayout(self.layout)

        self.update_json_fields()
        self.bottom_bar.update_status_indicator()
        self.form.update_url_label()

    def update_json_fields(self):
        if not self.server_running:
            if self.form.json_option_default.isChecked():
                self.form.json_input.setDisabled(True)
                self.form.json_input.setText(
                    json.dumps(
                        DEFAULT_JSON_RESPONSE,
                        indent=4,
                    )
                )
            else:
                self.form.json_input.setDisabled(False)
                self.form.json_input.setText(self.custom_json)

    def update_auth_fields(self):
        self.auth_type = self.form.auth_option_combo.currentText()
        if self.auth_type == 'JWT Bearer Auth':
            self.form.auth_info.set_text(
                f'<b>Token URL:</b> '
                f'http://localhost:{self.form.port_input.text() or "4000"}/token [POST]<br>'
                f'<b>Username:</b> {DEFAULT_USERNAME}<br>'
                f'<b>Password:</b> {DEFAULT_PASSWORD}<br>'
            )
        elif self.auth_type == 'Basic Auth':
            self.form.auth_info.set_text(
                f'<b>Username:</b> {DEFAULT_USERNAME}<br>'
                f'<b>Password:</b> {DEFAULT_PASSWORD}<br>'
            )
        elif self.auth_type == 'OAuth2':
            self.form.auth_info.set_text(
                f'<b>Token URL:</b> '
                f'http://localhost:{self.form.port_input.text() or "4000"}/token [POST]<br>'
                f'<b>client_id:</b> {DEFAULT_CLIENT_ID}<br>'
                f'<b>client_secret:</b> {DEFAULT_CLIENT_SECRET}<br>'
                f'<b>grant_type:</b> {GRANT_TYPE}<br>'
            )
        elif self.auth_type == 'API Key':
            self.form.auth_info.set_text(f'<b>X-API-KEY:</b> {DEFAULT_API_KEY}<br>')
        elif self.auth_type == 'Digest':
            self.form.auth_info.set_text(
                f'<b>Username:</b> {DEFAULT_USERNAME}<br>'
                f'<b>Password:</b> {DEFAULT_PASSWORD}<br>'
                f'<b>Realm:</b> {DEFAULT_REALM}<br>'
                f'<b>Algorithm:</b> {DIGEST_ALGORITHM}<br>'
                f'<b>qop:</b> {DIGEST_QOP}<br>'
            )
        else:
            self.form.auth_info.clear()

    def toggle_server(self):
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()

    def start_server(self):
        self.server_button.toggle_button.setDisabled(True)
        self.toggle_layout_form(True)
        self.setCursor(Qt.WaitCursor)

        QTimer.singleShot(0, self._start_server)

    def stop_server(self):
        self.server_button.toggle_button.setDisabled(True)
        self.setCursor(Qt.WaitCursor)

        QTimer.singleShot(0, self._stop_server)

    def _start_server(self):
        try:
            if self.server_instance:
                self.server_instance = None

            if self.form.json_option_custom.isChecked():
                self.custom_json = self.form.json_input.toPlainText()
                json_data = json.loads(self.custom_json)
            else:
                self.custom_json = json.dumps(
                    {'message': 'This is the default JSON response'},
                    indent=4,
                )
                json_data = json.loads(self.custom_json)

            port = (
                int(self.form.port_input.text())
                if self.form.port_input.text().isdigit()
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
            self.form.update_url_label()
            self.server_button.toggle_button.setText(self.tr('Stop Server'))
            self.server_running = True
            self.bottom_bar.update_status_indicator()
        except json.JSONDecodeError:
            QMessageBox.critical(self, 'Error', 'Invalid JSON format!')
            self.toggle_layout_form(False)
        finally:
            self.server_button.toggle_button.setDisabled(False)
            self.unsetCursor()

    def _stop_server(self):
        if self.server_instance:
            try:
                self.server_instance.stop()
                self.server_instance = None
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to stop the server: {str(e)}')
            finally:
                self.server_button.toggle_button.setText(self.tr('Start Server'))
                self.server_running = False
                self.toggle_layout_form(False)
                self.bottom_bar.update_status_indicator()
                self.server_button.toggle_button.setDisabled(False)
                self.unsetCursor()

    def toggle_layout_form(self, status):
        self.form.port_input.setDisabled(status)
        self.form.json_option_default.setDisabled(status)
        self.form.json_option_custom.setDisabled(status)
        self.form.auth_option_combo.setDisabled(status)
        self.form.import_json_button.setDisabled(status)

    def change_language(self):
        current_language = self.top_bar.language_selector.currentText()
        if current_language == 'English':
            self.translator.load("translations/en_US.qm")
            self.form.import_json_button.setFixedSize(120, 26)
        elif current_language == 'Portuguese':
            self.translator.load("translations/pt_BR.qm")
            self.form.import_json_button.setFixedSize(150, 26)
        elif current_language == 'Spanish':
            self.translator.load("translations/es_ES.qm")
            self.form.import_json_button.setFixedSize(150, 26)
        self.app.installTranslator(self.translator)
        self.retranslateUi()

    def retranslateUi(self):
        self.form.port_input.setPlaceholderText(
            self.tr('Enter port (default is 4000)')
        )
        self.form.auth_option_label.setText(self.tr('Authentication Type:'))
        self.form.json_option_label.setText(self.tr('JSON Response:'))
        self.form.json_option_default.setText(self.tr('Use default JSON'))
        self.form.json_option_custom.setText(self.tr('Write your own JSON'))
        self.form.import_json_button.setText(self.tr('Import JSON File'))
        self.form.json_input.setPlaceholderText(self.tr('Enter JSON here...'))
        self.form.port_label.setText(self.tr('Port:'))
        if self.server_running:
            self.bottom_bar.status_indicator.setText(tr('Active'))
            self.server_button.toggle_button.setText(self.tr('Stop Server'))
        else:
            self.server_button.toggle_button.setText(self.tr('Start Server'))
            self.bottom_bar.status_indicator.setText(tr('Inactive'))

        self.form.auth_option_combo.clear()
        self.form.auth_option_combo.addItems(
            [
                self.tr('None'),
                self.tr('Basic Auth'),
                self.tr('JWT Bearer Auth'),
                self.tr('OAuth2'),
                self.tr('API Key'),
                self.tr('Digest'),
            ]
        )
