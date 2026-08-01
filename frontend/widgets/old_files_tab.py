from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget, QLineEdit
from backend.old_file_detector import find_old_files
from frontend.widgets.folder_browser import FolderBrowser


class OldFilesTab(QWidget):
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

        days_row = QHBoxLayout()
        days_row.addWidget(QLabel("Kitne din se purani (days):"))
        self.days_input = QLineEdit()
        self.days_input.setPlaceholderText("jaise: 180")
        days_row.addWidget(self.days_input)
        layout.addLayout(days_row)

        find_button = QPushButton("Old Files Dhundo")
        find_button.clicked.connect(self.run_find)
        layout.addWidget(find_button)

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

    def run_find(self):
        self.result_list.clear()
        if not self.selected_folder:
            self.result_list.addItem("Pehle folder select karo!")
            return
        days_text = self.days_input.text().strip()
        days = int(days_text) if days_text.isdigit() else 180
        old_files = find_old_files(self.selected_folder, days_threshold=days)
        if not old_files:
            self.result_list.addItem(f"{days}+ din se purani koi file nahi mili.")
            return
        for item in old_files:
            self.result_list.addItem(f"{item['days_since_access']} din pehle  |  {item['path']}")