from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QIntValidator


class PortInput(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText('Enter port (default is 4000)')
        self.setValidator(QIntValidator(1, 65535))
