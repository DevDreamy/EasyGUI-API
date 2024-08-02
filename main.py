import sys
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.main_window import MainWindow

translator = QTranslator()


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("src/resources/icons/easy_gui_api_icon.ico"))
    translator.load("translations/en_US.qm")
    app.installTranslator(translator)

    main_window = MainWindow(app, translator)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
