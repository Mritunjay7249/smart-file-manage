import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QDateEdit, QCheckBox, QTreeWidget,
    QTreeWidgetItem, QFileDialog
)
from PyQt6.QtCore import QDate, Qt, QThread, pyqtSignal
from datetime import datetime
from backend.search import advanced_search_iter


EXTENSIONS = [
    "Any",
    ".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg",
    ".mp4", ".mkv", ".avi", ".mov", ".webm",
    ".mp3", ".wav", ".flac",
    ".zip", ".rar", ".7z", ".tar",
    ".exe", ".msi", ".apk", ".bat", ".dmg",
    ".py", ".js", ".html", ".css", ".json", ".java", ".cpp",
]


class SearchWorker(QThread):
    """Background thread jo search chalata hai, taaki UI freeze na ho."""
    result_found = pyqtSignal(dict)
    finished_search = pyqtSignal(int)

    def __init__(self, folder, filters):
        super().__init__()
        self.folder = folder
        self.filters = filters
        self.stop_flag = [False]

    def run(self):
        count = 0
        for result in advanced_search_iter(self.folder, stop_flag=self.stop_flag, **self.filters):
            self.result_found.emit(result)
            count += 1
            if count >= 500:   # safety cap - itni saari results dikhana bhi useless hai
                break
        self.finished_search.emit(count)

    def stop(self):
        self.stop_flag[0] = True


class SearchTab(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.selected_folder = state.selected_folder
        self.worker = None
        self.init_ui()
        state.folder_changed.connect(self.on_folder_changed)
        if self.selected_folder:
            self.on_folder_changed(self.selected_folder)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        folder_row = QHBoxLayout()
        self.folder_label = QLabel("Koi folder select nahi — search 'This PC' mein hogi (thodi slow, folder chunna faster hai)")
        folder_row.addWidget(self.folder_label)
        choose_btn = QPushButton("Folder Choose Karo")
        choose_btn.clicked.connect(self.choose_folder)
        folder_row.addWidget(choose_btn)
        layout.addLayout(folder_row)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Naam mein:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("jaise: wire")
        row1.addWidget(self.name_input)

        row1.addWidget(QLabel("Type:"))
        self.ext_combo = QComboBox()
        self.ext_combo.addItems(EXTENSIONS)
        self.ext_combo.addItem("Custom...")
        self.ext_combo.currentTextChanged.connect(self.on_ext_changed)
        row1.addWidget(self.ext_combo)

        self.custom_ext_input = QLineEdit()
        self.custom_ext_input.setPlaceholderText(".xyz")
        self.custom_ext_input.setMaximumWidth(80)
        self.custom_ext_input.setVisible(False)
        row1.addWidget(self.custom_ext_input)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Size (KB) — Min:"))
        self.min_size_input = QLineEdit()
        row2.addWidget(self.min_size_input)
        row2.addWidget(QLabel("Max:"))
        self.max_size_input = QLineEdit()
        row2.addWidget(self.max_size_input)
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        self.date_checkbox = QCheckBox("Date se filter karo:")
        self.date_checkbox.stateChanged.connect(self.toggle_date_filter)
        row3.addWidget(self.date_checkbox)
        row3.addWidget(QLabel("Iske baad:"))
        self.date_after = QDateEdit()
        self.date_after.setCalendarPopup(True)
        self.date_after.setDate(QDate.currentDate().addMonths(-1))
        self.date_after.setEnabled(False)
        row3.addWidget(self.date_after)
        row3.addWidget(QLabel("Iske pehle:"))
        self.date_before = QDateEdit()
        self.date_before.setCalendarPopup(True)
        self.date_before.setDate(QDate.currentDate())
        self.date_before.setEnabled(False)
        row3.addWidget(self.date_before)
        layout.addLayout(row3)

        btn_row = QHBoxLayout()
        self.search_button = QPushButton("🔎  Search Karo")
        self.search_button.clicked.connect(self.run_search)
        btn_row.addWidget(self.search_button)

        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        btn_row.addWidget(self.stop_button)
        layout.addLayout(btn_row)

        self.result_tree = QTreeWidget()
        self.result_tree.setHeaderLabels(["Name", "Size", "Modified", "Path"])
        self.result_tree.setColumnWidth(0, 250)
        self.result_tree.setColumnWidth(1, 80)
        self.result_tree.setColumnWidth(2, 140)
        layout.addWidget(self.result_tree)

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(self.count_label)

    def on_ext_changed(self, text):
        self.custom_ext_input.setVisible(text == "Custom...")

    def toggle_date_filter(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.date_after.setEnabled(enabled)
        self.date_before.setEnabled(enabled)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Folder Chuno")
        if folder:
            self.state.set_folder(folder)

    def on_folder_changed(self, path):
        self.selected_folder = path
        self.folder_label.setText(f"Search karenge yahan: {path}")

    def run_search(self):
        self.result_tree.clear()
        search_root = self.selected_folder or "C:\\"

        name = self.name_input.text().strip() or None
        ext_choice = self.ext_combo.currentText()
        if ext_choice == "Custom...":
            ext = self.custom_ext_input.text().strip()
            if ext and not ext.startswith("."):
                ext = "." + ext
            ext = ext or None
        elif ext_choice == "Any":
            ext = None
        else:
            ext = ext_choice

        min_size = self.min_size_input.text().strip()
        max_size = self.max_size_input.text().strip()
        min_size = float(min_size) if min_size.replace(".", "", 1).isdigit() else None
        max_size = float(max_size) if max_size.replace(".", "", 1).isdigit() else None

        date_after = date_before = None
        if self.date_checkbox.isChecked():
            qd_a, qd_b = self.date_after.date(), self.date_before.date()
            date_after = datetime(qd_a.year(), qd_a.month(), qd_a.day())
            date_before = datetime(qd_b.year(), qd_b.month(), qd_b.day(), 23, 59, 59)

        filters = dict(name_contains=name, extension=ext, min_size_kb=min_size,
                        max_size_kb=max_size, date_after=date_after, date_before=date_before)

        self.worker = SearchWorker(search_root, filters)
        self.worker.result_found.connect(self.add_result)
        self.worker.finished_search.connect(self.search_done)
        self.worker.start()

        self.search_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.count_label.setText("Dhund raha hai...")

    def add_result(self, r):
        size_str = f"{r['size_kb']:.1f} KB"
        date_str = r["modified"].strftime("%Y-%m-%d %H:%M")
        item = QTreeWidgetItem([r["name"], size_str, date_str, r["path"]])
        self.result_tree.addTopLevelItem(item)

    def search_done(self, count):
        self.count_label.setText(f"{count} file(s) mili" + (" (500 pe rok diya, aur specific search karo)" if count >= 500 else ""))
        self.search_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def stop_search(self):
        if self.worker:
            self.worker.stop()
        self.stop_button.setEnabled(False)
        self.count_label.setText("Rok diya.")