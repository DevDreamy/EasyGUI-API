from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from ..ui_elements import (
    StatusIndicator, 
)


class BottomBar(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()

        self.credits_label = QLabel(
            '<a'
            ' style="text-decoration:none;color:#555555;"'
            ' href="https://github.com/DevDreamy">DevDreamy'
            '</a>'
        )
        self.credits_label.setOpenExternalLinks(True)
        self.credits_label.setTextFormat(Qt.TextFormat.RichText)
        self.credits_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(self.credits_label)

        self.status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        self.status_layout.addWidget(self.status_indicator)
        self.layout.addLayout(self.status_layout)

        self.setLayout(self.layout)

    def update_status_indicator(self):
        if self.main_window.server_running:
            self.status_indicator.set_active()
            self.status_indicator.setText(self.tr('Active'))
        else:
            self.status_indicator.setText(self.tr('Inactive'))
            self.status_indicator.set_inactive()