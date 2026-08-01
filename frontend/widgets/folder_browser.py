import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt


class FolderBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.current_path = None
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list = QListWidget()
        self.list.setFixedHeight(180)
        self.list.itemDoubleClicked.connect(self.on_double_click)
        layout.addWidget(self.list)

    def show_folder(self, path):
        if not path or not os.path.isdir(path):
            return
        self.current_path = path
        self.list.clear()

        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return

        for name in items:
            full_path = os.path.join(path, name)
            icon = "📁" if os.path.isdir(full_path) else "📄"
            item = QListWidgetItem(f"{icon}  {name}")
            item.setData(Qt.ItemDataRole.UserRole, full_path)
            self.list.addItem(item)

    def on_double_click(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if os.path.isdir(path):
            self.show_folder(path)