import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem, QSplitter, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime


class ExplorerView(QWidget):
    """
    Poora Explorer-style file browser: sidebar + nav bar + table view.
    folder_opened signal se baaki app ko batata hai konsa folder khula.
    """
    folder_opened = pyqtSignal(str)

    QUICK_ACCESS = ["Desktop", "Downloads", "Documents", "Pictures", "Music", "Videos"]

    def __init__(self, start_path=None):
        super().__init__()
        self.current_path = start_path or os.path.expanduser("~")
        self.history = []
        self.forward_stack = []
        self.sort_column = 0
        self.sort_reverse = False
        self.init_ui()
        self.load_folder(self.current_path)

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # --- Nav bar ---
        nav_row = QHBoxLayout()
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedWidth(36)
        self.back_btn.clicked.connect(self.go_back)
        nav_row.addWidget(self.back_btn)

        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedWidth(36)
        self.forward_btn.clicked.connect(self.go_forward)
        nav_row.addWidget(self.forward_btn)

        self.up_btn = QPushButton("↑")
        self.up_btn.setFixedWidth(36)
        self.up_btn.clicked.connect(self.go_up)
        nav_row.addWidget(self.up_btn)

        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setFixedWidth(36)
        self.refresh_btn.clicked.connect(lambda: self.load_folder(self.current_path))
        nav_row.addWidget(self.refresh_btn)

        self.path_bar = QLineEdit()
        self.path_bar.returnPressed.connect(self.path_bar_entered)
        nav_row.addWidget(self.path_bar)

        main_layout.addLayout(nav_row)

        # --- Sidebar + Table (splitter se side by side) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(160)
        self.build_sidebar()
        self.sidebar.itemClicked.connect(self.sidebar_clicked)
        splitter.addWidget(self.sidebar)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Size", "Modified"])
        self.tree.setColumnWidth(0, 320)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 90)
        self.tree.itemDoubleClicked.connect(self.item_double_clicked)
        self.tree.header().sectionClicked.connect(self.header_clicked)
        splitter.addWidget(self.tree)

        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #a6adc8; font-size: 12px;")
        main_layout.addWidget(self.info_label)

    def build_sidebar(self):
        home = os.path.expanduser("~")
        for name in self.QUICK_ACCESS:
            path = os.path.join(home, name)
            item = QListWidgetItem(f"📁  {name}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.sidebar.addItem(item)

    def sidebar_clicked(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if os.path.isdir(path):
            self.navigate_to(path)

    # ---------- Core loading ----------

    def load_folder(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            self.info_label.setText(f"Khul nahi saka: {path}")
            return

        self.current_path = path
        self.path_bar.setText(path)
        self.tree.clear()

        try:
            names = os.listdir(path)
        except PermissionError:
            self.info_label.setText("Permission nahi hai.")
            return

        rows = []
        for name in names:
            full_path = os.path.join(path, name)
            is_dir = os.path.isdir(full_path)
            try:
                size = 0 if is_dir else os.path.getsize(full_path)
                modified = os.path.getmtime(full_path)
            except OSError:
                continue
            rows.append({
                "name": name, "path": full_path, "is_dir": is_dir,
                "size": size, "modified": modified
            })

        rows = self.sort_rows(rows)

        for row in rows:
            icon = "📁" if row["is_dir"] else self.get_icon(row["name"])
            type_str = "Folder" if row["is_dir"] else (os.path.splitext(row["name"])[1] or "File")
            size_str = "" if row["is_dir"] else self.format_size(row["size"])
            mod_str = datetime.fromtimestamp(row["modified"]).strftime("%Y-%m-%d %H:%M")

            item = QTreeWidgetItem([f"{icon}  {row['name']}", type_str, size_str, mod_str])
            item.setData(0, Qt.ItemDataRole.UserRole, row["path"])
            self.tree.addTopLevelItem(item)

        folder_count = sum(1 for r in rows if r["is_dir"])
        file_count = len(rows) - folder_count
        self.info_label.setText(f"{folder_count} folder(s), {file_count} file(s)")

        self.folder_opened.emit(path)

    def sort_rows(self, rows):
        keys = ["name", "type", "size", "modified"]
        key = keys[self.sort_column] if self.sort_column < len(keys) else "name"

        if key == "type":
            rows.sort(key=lambda r: (not r["is_dir"], os.path.splitext(r["name"])[1].lower()), reverse=self.sort_reverse)
        elif key == "size":
            rows.sort(key=lambda r: r["size"], reverse=self.sort_reverse)
        elif key == "modified":
            rows.sort(key=lambda r: r["modified"], reverse=self.sort_reverse)
        else:
            rows.sort(key=lambda r: (not r["is_dir"], r["name"].lower()), reverse=self.sort_reverse)
        return rows

    def header_clicked(self, column):
        if column == self.sort_column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.load_folder(self.current_path)

    def get_icon(self, file_name):
        ext = os.path.splitext(file_name)[1].lower()
        mapping = {
            "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
            "video": [".mp4", ".mkv", ".avi", ".mov"],
            "audio": [".mp3", ".wav", ".flac"],
            "pdf": [".pdf"], "doc": [".docx", ".doc", ".txt"],
            "zip": [".zip", ".rar", ".7z"], "code": [".py", ".js", ".html", ".css"],
        }
        icons = {"image": "🖼️", "video": "🎬", "audio": "🎵", "pdf": "📕", "doc": "📄", "zip": "🗜️", "code": "💻"}
        for key, exts in mapping.items():
            if ext in exts:
                return icons[key]
        return "📃"

    def format_size(self, size_bytes):
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    # ---------- Navigation ----------

    def navigate_to(self, path):
        self.history.append(self.current_path)
        self.forward_stack.clear()
        self.load_folder(path)

    def item_double_clicked(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if os.path.isdir(path):
            self.navigate_to(path)

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.navigate_to(parent)

    def go_back(self):
        if self.history:
            self.forward_stack.append(self.current_path)
            self.load_folder(self.history.pop())

    def go_forward(self):
        if self.forward_stack:
            self.history.append(self.current_path)
            self.load_folder(self.forward_stack.pop())

    def path_bar_entered(self):
        typed = self.path_bar.text().strip()
        if os.path.exists(typed):
            self.navigate_to(typed)
        else:
            self.info_label.setText("Yeh path exist nahi karta!")