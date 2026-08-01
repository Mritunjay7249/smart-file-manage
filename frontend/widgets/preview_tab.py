from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit
from backend.preview import preview_file, get_file_info


class PreviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)   
        layout.setSpacing(12)

        choose_button = QPushButton("File Choose Karo")
        choose_button.clicked.connect(self.choose_file)
        layout.addWidget(choose_button)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addWidget(self.output_box)

    def choose_file(self):
        # getOpenFileName ek FILE choose karata hai (folder nahi)
        file_path, _ = QFileDialog.getOpenFileName(self, "File Chuno")

        if not file_path:
            return

        info = get_file_info(file_path)
        self.output_box.clear()
        self.output_box.append(f"Name: {info['name']}")
        self.output_box.append(f"Size: {info['size']}")
        self.output_box.append(f"Extension: {info['extension']}\n")

        # Text file ho to content bhi dikhao
        if info['extension'].lower() in [".txt", ".py", ".md", ".csv", ".json", ".log"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(500)
            self.output_box.append("Content:\n" + content)
        else:
            self.output_box.append("(Iss file type ka text preview nahi hai)")