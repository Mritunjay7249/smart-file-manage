from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget, QLineEdit
from backend.tagger import tag_folder, search_by_tag
from frontend.widgets.folder_browser import FolderBrowser


class TaggerTab(QWidget):
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

        tag_button = QPushButton("Files Tag Karo")
        tag_button.clicked.connect(self.run_tagging)
        layout.addWidget(tag_button)

        search_row = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("tag naam, jaise: resume")
        search_row.addWidget(self.tag_input)
        search_button = QPushButton("Tag Se Search Karo")
        search_button.clicked.connect(self.run_search)
        search_row.addWidget(search_button)
        layout.addLayout(search_row)

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

    def run_tagging(self):
        self.result_list.clear()
        if not self.selected_folder:
            self.result_list.addItem("Pehle folder select karo!")
            return
        tag_folder(self.selected_folder)
        self.result_list.addItem("Tagging complete! ✅")

    def run_search(self):
        self.result_list.clear()
        tag = self.tag_input.text().strip()
        if not tag:
            self.result_list.addItem("Tag naam likho!")
            return
        results = search_by_tag(tag)
        if not results:
            self.result_list.addItem(f"'{tag}' se koi file nahi mili.")
        for path in results:
            self.result_list.addItem(path)