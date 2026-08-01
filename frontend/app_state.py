from PyQt6.QtCore import QObject, pyqtSignal


class AppState(QObject):
    folder_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.selected_folder = None

    def set_folder(self, path):
        self.selected_folder = path
        self.folder_changed.emit(path)