import os
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt

SETTINGS_FILE = "database/settings.json"


class DashboardTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.background_pixmap = None
        self.load_settings()
        self.init_ui()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                bg_path = settings.get("background_path")
                if bg_path and os.path.exists(bg_path):
                    self.background_pixmap = QPixmap(bg_path)
            except Exception:
                pass

    def save_settings(self, bg_path):
        os.makedirs("database", exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"background_path": bg_path}, f)

    def paintEvent(self, event):
        """Background image ko is tab ke andar hi draw karte hain"""
        painter = QPainter(self)
        if self.background_pixmap and not self.background_pixmap.isNull():
            scaled = self.background_pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

            painter.setOpacity(0.5)
            painter.fillRect(self.rect(), Qt.GlobalColor.black)
        else:
            painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        super().paintEvent(event)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Card jaisa semi-transparent container, taaki background pe text padhne layak rahe
        card = QWidget()
        card.setStyleSheet("background-color: rgba(24, 24, 37, 190); border-radius: 14px;")
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(8)

        title = QLabel("Smart File Manager")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #89b4fa; background: transparent;")
        card_layout.addWidget(title)

        subtitle = QLabel("Apni files ko organize, search, aur secure karo — sab ek jagah.")
        subtitle.setStyleSheet("font-size: 14px; color: #a6adc8; background: transparent;")
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(15)

        bg_row = QHBoxLayout()
        bg_button = QPushButton("Background Badlo")
        bg_button.clicked.connect(self.change_background)
        bg_row.addWidget(bg_button)

        clear_button = QPushButton("Default Background")
        clear_button.clicked.connect(self.reset_background)
        bg_row.addWidget(clear_button)
        bg_row.addStretch()
        card_layout.addLayout(bg_row)

        card_layout.addSpacing(15)

        features = [
            "Files — Real file browser jaisa Explorer",
            "Organize — Files ko type ke hisaab se sort karo",
            "Duplicates — Same files dhundo aur hatao",
            "Rename — Bulk mein files rename karo",
            "Tags — Smart tagging aur search",
            "Storage — Dekho kaun si files zyada space le rahi hain",
            "Old Files — Purani, unused files dhundo",
            "Search — Advanced filters se files dhundo",
            "Cleanup — Auto-delete rules banao",
            "Security — Files encrypt/decrypt karo",
        ]

        for f in features:
            label = QLabel(f)
            label.setStyleSheet("font-size: 13px; padding: 5px 0px; color: #cdd6f4; background: transparent;")
            card_layout.addWidget(label)

        layout.addWidget(card)

    def change_background(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Background Image Chuno", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if file_path:
            self.background_pixmap = QPixmap(file_path)
            self.save_settings(file_path)
            self.update()

    def reset_background(self):
        self.background_pixmap = None
        self.save_settings(None)
        self.update()