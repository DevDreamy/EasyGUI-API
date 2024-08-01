from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class AuthInfo(QLabel):
    def __init__(self):
        super().__init__()
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

    def set_text(self, text):
        self.setText(text)
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

    def clear(self):
        self.setText('')
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
