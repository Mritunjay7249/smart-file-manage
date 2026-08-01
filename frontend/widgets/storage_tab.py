from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget
from backend.storage_analyzer import analyze_storage, format_size
from frontend.widgets.folder_browser import FolderBrowser


class StorageTab(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.selected_folder = state.selected_folder
        self.init_ui()
        state.folder_changed.connect(self.on_folder_changed)
        if self.selected_folder:
            self.on_folder_changed(self.selected_folder)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.folder_label = QLabel("Koi folder select nahi hua")
        layout.addWidget(self.folder_label)

        choose_button = QPushButton("Folder Choose Karo")
        choose_button.clicked.connect(self.choose_folder)
        layout.addWidget(choose_button)

        self.browser = FolderBrowser()
        layout.addWidget(self.browser)

        analyze_button = QPushButton("Storage Analyze Karo")
        analyze_button.clicked.connect(self.run_analyze)
        layout.addWidget(analyze_button)

        self.result_list = QListWidget()
        layout.addWidget(self.result_list)

    def on_folder_changed(self, path):
        self.selected_folder = path
        self.folder_label.setText(f"Selected: {path}")
        self.browser.show_folder(path)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Folder Chuno")
        if folder:
            self.state.set_folder(folder)

    def run_analyze(self):
        self.result_list.clear()
        if not self.selected_folder:
            self.result_list.addItem("Pehle folder select karo!")
            return
        results = analyze_storage(self.selected_folder)
        total = sum(item["size_bytes"] for item in results)
        self.result_list.addItem(f"Total: {format_size(total)}")
        for item in results:
            icon = "[Folder]" if item["type"] == "folder" else "[File]"
            self.result_list.addItem(f"{icon} {item['size_readable']}  —  {item['name']}")
    