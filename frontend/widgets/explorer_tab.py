import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QLineEdit
)
from PyQt6.QtCore import Qt


class ExplorerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_path = os.path.expanduser("~")   # start = user's home folder
        self.history = []       # peeche jaane ke liye stack
        self.forward_stack = [] # aage jaane ke liye stack
        self.init_ui()
        self.load_folder(self.current_path)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Top row: Back, Forward, Up buttons + path bar
        nav_row = QHBoxLayout()
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedWidth(40)
        self.back_btn.clicked.connect(self.go_back)
        nav_row.addWidget(self.back_btn)

        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedWidth(40)
        self.forward_btn.clicked.connect(self.go_forward)
        nav_row.addWidget(self.forward_btn)

        self.up_btn = QPushButton("↑")
        self.up_btn.setFixedWidth(40)
        self.up_btn.clicked.connect(self.go_up)
        nav_row.addWidget(self.up_btn)

        self.path_bar = QLineEdit()
        self.path_bar.returnPressed.connect(self.path_bar_entered)  # Enter dabane pe
        nav_row.addWidget(self.path_bar)

        layout.addLayout(nav_row)

        # File/folder list
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.item_double_clicked)
        layout.addWidget(self.file_list)

        # Bottom info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(self.info_label)

    def load_folder(self, path):
        """Diye gaye folder ka content list mein dikhata hai"""
        if not os.path.exists(path) or not os.path.isdir(path):
            self.info_label.setText(f"Yeh folder nahi khul saka: {path}")
            return

        self.current_path = path
        self.path_bar.setText(path)
        self.file_list.clear()

        try:
            items = os.listdir(path)
        except PermissionError:
            self.info_label.setText("Permission nahi hai is folder ko kholne ki.")
            return

        # Pehle folders dikhao, phir files (dono alphabetically sorted)
        folders = sorted([i for i in items if os.path.isdir(os.path.join(path, i))])
        files = sorted([i for i in items if os.path.isfile(os.path.join(path, i))])

        for folder_name in folders:
            item = QListWidgetItem(f"📁  {folder_name}")
            item.setData(Qt.ItemDataRole.UserRole, os.path.join(path, folder_name))
            self.file_list.addItem(item)

        for file_name in files:
            icon = self.get_icon(file_name)
            item = QListWidgetItem(f"{icon}  {file_name}")
            item.setData(Qt.ItemDataRole.UserRole, os.path.join(path, file_name))
            self.file_list.addItem(item)

        self.info_label.setText(f"{len(folders)} folder(s), {len(files)} file(s)")

    def get_icon(self, file_name):
        """Extension ke hisaab se ek chhota emoji icon deta hai"""
        ext = os.path.splitext(file_name)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            return "🖼️"
        elif ext in [".mp4", ".mkv", ".avi", ".mov"]:
            return "🎬"
        elif ext in [".mp3", ".wav", ".flac"]:
            return "🎵"
        elif ext in [".pdf"]:
            return "📕"
        elif ext in [".docx", ".doc", ".txt"]:
            return "📄"
        elif ext in [".zip", ".rar", ".7z"]:
            return "🗜️"
        elif ext in [".py", ".js", ".html", ".css"]:
            return "💻"
        else:
            return "📃"

    def item_double_clicked(self, item):
        """Jab kisi item pe double-click ho"""
        clicked_path = item.data(Qt.ItemDataRole.UserRole)

        if os.path.isdir(clicked_path):
            self.history.append(self.current_path)  # current path yaad rakho "back" ke liye
            self.forward_stack.clear()               # naya navigation hua, forward stack reset
            self.load_folder(clicked_path)
        else:
            self.info_label.setText(f"File: {clicked_path} (preview ke liye 'Preview' tab use karo)")

    def go_up(self):
        """Ek level upar (parent folder) jao"""
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.history.append(self.current_path)
            self.forward_stack.clear()
            self.load_folder(parent)

    def go_back(self):
        if self.history:
            self.forward_stack.append(self.current_path)
            previous = self.history.pop()
            self.load_folder(previous)

    def go_forward(self):
        if self.forward_stack:
            self.history.append(self.current_path)
            next_path = self.forward_stack.pop()
            self.load_folder(next_path)

    def path_bar_entered(self):
        """Jab user path bar mein khud path type karke Enter dabaye"""
        typed_path = self.path_bar.text().strip()
        if os.path.exists(typed_path):
            self.history.append(self.current_path)
            self.forward_stack.clear()
            self.load_folder(typed_path)
        else:
            self.info_label.setText("Yeh path exist nahi karta!")