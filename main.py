import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QColor, QFont
from PyQt6.QtCore import Qt
from frontend.main_window import MainWindow


def resource_path(relative_path):
    """
    Normal Python se chalte waqt aur PyInstaller exe se chalte waqt,
    files ka path alag hota hai. Yeh function dono cases mein sahi path deta hai.
    """
    try:
        base_path = sys._MEIPASS   # PyInstaller yeh temp folder banata hai exe chalte waqt
    except AttributeError:
        base_path = os.path.abspath(".")   # normal Python run ke liye
    return os.path.join(base_path, relative_path)


def get_app_data_dir():
    """
    Database/settings jaisi cheezein jo LIKHNI (write) hain, unhe temp folder mein
    nahi, balki exe ke bagal mein ek permanent 'database' folder mein rakhna hai.
    """
    if getattr(sys, 'frozen', False):
        # exe se chal rahi hai
        base = os.path.dirname(sys.executable)
    else:
        # normal python se chal rahi hai
        base = os.path.abspath(".")
    return os.path.join(base, "database")


def create_app_icon():
    db_dir = get_app_data_dir()
    os.makedirs(db_dir, exist_ok=True)
    icon_path = os.path.join(db_dir, "app_icon.png")

    if not os.path.exists(icon_path):
        pixmap = QPixmap(128, 128)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#89b4fa"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(8, 8, 112, 112, 24, 24)
        painter.setPen(QColor("#1e1e2e"))
        painter.setFont(QFont("Segoe UI", 50, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "SF")
        painter.end()
        pixmap.save(icon_path)

    return QIcon(icon_path)


def handle_error(exc_type, exc_value, exc_traceback):
    print(f"Error: {exc_type.__name__}: {exc_value}")


sys.excepthook = handle_error


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(create_app_icon())

    style_path = resource_path("frontend/styles.qss")
    with open(style_path, "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.setWindowIcon(create_app_icon())
    window.show()
    sys.exit(app.exec())