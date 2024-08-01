from PyQt5.QtCore import QCoreApplication


def tr(text):
    return QCoreApplication.translate("MainWindow", text)
