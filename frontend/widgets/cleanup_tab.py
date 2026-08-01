from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget, QLineEdit
from backend.cleanup_rules import add_rule, apply_all_rules
from frontend.widgets.folder_browser import FolderBrowser


class CleanupTab(QWidget):
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

        row = QHBoxLayout()
        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText("extension, jaise .exe (khali chodo = sab)")
        row.addWidget(self.ext_input)
        self.days_input = QLineEdit()
        self.days_input.setPlaceholderText("kitne din purani (jaise 7)")
        row.addWidget(self.days_input)
        layout.addLayout(row)

        add_button = QPushButton("Rule Add Karo")
        add_button.clicked.connect(self.add_new_rule)
        layout.addWidget(add_button)

        preview_button = QPushButton("Preview Karo (Dry Run)")
        preview_button.clicked.connect(self.run_preview)
        layout.addWidget(preview_button)

        apply_button = QPushButton("⚠ ASLI DELETE KARO")
        apply_button.clicked.connect(self.run_apply)
        layout.addWidget(apply_button)

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

    def add_new_rule(self):
        self.result_list.clear()
        if not self.selected_folder:
            self.result_list.addItem("Pehle folder select karo!")
            return
        ext = self.ext_input.text().strip() or None
        days_text = self.days_input.text().strip()
        days = int(days_text) if days_text.isdigit() else 7
        add_rule(self.selected_folder, older_than_days=days, extension=ext, action="delete")
        self.result_list.addItem(f"Rule add ho gaya: {ext or 'sab files'}, {days}+ din purani")

    def run_preview(self):
        self.result_list.clear()
        apply_all_rules(dry_run=True)
        self.result_list.addItem("Terminal mein detail dekh sakte ho.")
        self.result_list.addItem("Preview complete — koi file delete nahi hui.")

    def run_apply(self):
        self.result_list.clear()
        apply_all_rules(dry_run=False)
        self.result_list.addItem("Rules apply ho gaye.")
        if self.selected_folder:
            self.browser.show_folder(self.selected_folder)