from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt


class ServerButton(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()

        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.toggle_button = QPushButton(self.tr('Start Server'))
        self.toggle_button.setFixedSize(200, 40)
        self.toggle_button.setStyleSheet("font-size: 14px; padding: 8px;")
        self.toggle_button.clicked.connect(self.main_window.toggle_server)
        self.layout.addWidget(self.toggle_button)

        self.setLayout(self.layout)