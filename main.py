import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/easy_gui_api_icon.ico"))
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
