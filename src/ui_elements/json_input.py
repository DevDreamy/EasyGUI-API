from PyQt6.QtWidgets import QTextEdit

class JsonInput(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText('Enter JSON here...')