from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class StatusIndicator(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedSize(80, 30)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            'border-radius: 15px; '
            'color: white; '
            'background-color: red; '
            'text-align: center; '
            'font-weight: bold; '
            'padding: 5px; '
        )

    def set_active(self):
        self.setText('Active')
        self.setStyleSheet(
            'background-color: green;'
            'color: white;'
            'border-radius: 15px;'
            'padding: 3px;'
            'text-align: center;'
            'font-weight: bold;'
        )

    def set_inactive(self):
        self.setText('Inactive')
        self.setStyleSheet(
            'background-color: red;'
            'color: white;'
            'border-radius: 15px;'
            'padding: 3px;'
            'text-align:'
            'center;'
            'font-weight: bold;'
        )
