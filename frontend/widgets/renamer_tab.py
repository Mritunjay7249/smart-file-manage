from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget, QLineEdit
from backend.renamer import bulk_rename
from frontend.widgets.folder_browser import FolderBrowser


class RenamerTab(QWidget):
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

        prefix_row = QHBoxLayout()
        prefix_row.addWidget(QLabel("Prefix:"))
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("jaise: Holiday")
        prefix_row.addWidget(self.prefix_input)
        layout.addLayout(prefix_row)

        rename_button = QPushButton("Rename Karo")
        rename_button.clicked.connect(self.run_rename)
        layout.addWidget(rename_button)

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

    def run_rename(self):
        self.result_list.clear()
        if not self.selected_folder:
            self.result_list.addItem("Pehle folder select karo!")
            return
        prefix = self.prefix_input.text().strip()
        if not prefix:
            self.result_list.addItem("Prefix likho pehle!")
            return
        bulk_rename(self.selected_folder, prefix=prefix)
        self.result_list.addItem(f"Rename ho gaya prefix '{prefix}' ke saath! ✅")
        self.browser.show_folder(self.selected_folder)