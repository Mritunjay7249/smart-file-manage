from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget
from backend.security import generate_key, encrypt_file, decrypt_file
import os


class SecurityTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)   
        layout.setSpacing(12)

        key_button = QPushButton("Encryption Key Banao (sirf pehli baar)")
        key_button.clicked.connect(self.make_key)
        layout.addWidget(key_button)

        encrypt_button = QPushButton("File Encrypt Karo (Lock)")
        encrypt_button.clicked.connect(self.run_encrypt)
        layout.addWidget(encrypt_button)

        decrypt_button = QPushButton("File Decrypt Karo (Unlock)")
        decrypt_button.clicked.connect(self.run_decrypt)
        layout.addWidget(decrypt_button)

        self.result_list = QListWidget()
        layout.addWidget(self.result_list)

    def make_key(self):
        self.result_list.clear()
        generate_key()
        if os.path.exists("database/secret.key"):
            self.result_list.addItem("Key ready hai. ✅")

    def run_encrypt(self):
        self.result_list.clear()
        file_path, _ = QFileDialog.getOpenFileName(self, "File Chuno")
        if not file_path:
            return
        encrypt_file(file_path)
        self.result_list.addItem(f"Encrypted: {file_path}")

    def run_decrypt(self):
        self.result_list.clear()
        file_path, _ = QFileDialog.getOpenFileName(self, "File Chuno")
        if not file_path:
            return
        decrypt_file(file_path)
        self.result_list.addItem(f"Decrypted: {file_path}")