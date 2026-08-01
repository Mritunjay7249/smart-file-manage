from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget
from backend.duplicates import find_duplicates
from frontend.widgets.folder_browser import FolderBrowser
from PyQt6.QtWidgets import QApplication   # NAYA IMPORT upar


class DuplicatesTab(QWidget):
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

        find_button = QPushButton("Duplicates Dhundo")
        find_button.clicked.connect(self.run_find_duplicates)
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

    def run_find_duplicates(self):
        self.result_list.clear()

        if not self.selected_folder:
            self.result_list.addItem("Pehle ek folder select karo!")
            return
        duplicates = find_duplicates(self.selected_folder)
        if not duplicates:
            self.result_list.addItem("Koi duplicate file nahi mili.")
            return
        for i, (file_hash, paths) in enumerate(duplicates.items(), start=1):
            self.result_list.addItem(f"--- Group {i} ---")
            for path in paths:
                self.result_list.addItem(f"    {path}")
        