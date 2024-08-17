from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtGui import  QIcon
from PyQt5.QtCore import Qt
from ..utils import brazil_flag, usa_flag, spain_flag


class TopBar(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()

        self.url_label = QLabel()
        self.url_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.layout.addWidget(self.url_label)

        self.language_selector = QComboBox()
        self.language_selector.addItem(QIcon(usa_flag), "English")
        self.language_selector.addItem(QIcon(brazil_flag), "Portuguese")
        self.language_selector.addItem(QIcon(spain_flag), "Spanish")
        self.language_selector.setFixedWidth(120)
        self.language_selector.currentIndexChanged.connect(self.main_window.change_language)
        self.layout.addWidget(
            self.language_selector, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.setLayout(self.layout)