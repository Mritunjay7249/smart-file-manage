import os
import json
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt

from frontend.app_state import AppState
from frontend.widgets.dashboard_tab import DashboardTab
from frontend.widgets.explorer_view import ExplorerView
from frontend.widgets.organize_tab import OrganizeTab
from frontend.widgets.duplicates_tab import DuplicatesTab
from frontend.widgets.renamer_tab import RenamerTab
from frontend.widgets.preview_tab import PreviewTab
from frontend.widgets.tagger_tab import TaggerTab
from frontend.widgets.storage_tab import StorageTab
from frontend.widgets.old_files_tab import OldFilesTab
from frontend.widgets.search_tab import SearchTab
from frontend.widgets.cleanup_tab import CleanupTab
from frontend.widgets.security_tab import SecurityTab
from frontend.widgets.leftover_tab import LeftoverTab
SETTINGS_FILE = "database/settings.json"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart File Manager")
        self.setGeometry(100, 100, 1100, 700)
        self.setMinimumSize(950, 600)
        self.state = AppState()
        self.background_pixmap = None

        self.load_settings()
        self.init_ui()

    def load_settings(self):
        """Pehle se saved background path load karo (agar hai)"""
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

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(DashboardTab(self), "🏠 Home")   # NOTE: self pass kiya, background change karne ke liye

        self.explorer = ExplorerView()
        self.explorer.folder_opened.connect(self.state.set_folder)
        self.tabs.addTab(self.explorer, "🗂️ Files")

        self.tabs.addTab(OrganizeTab(self.state), "📁 Organize")
        self.tabs.addTab(DuplicatesTab(self.state), "🔍 Duplicates")
        self.tabs.addTab(RenamerTab(self.state), "✏️ Rename")
        self.tabs.addTab(PreviewTab(), "👁️ Preview")
        self.tabs.addTab(TaggerTab(self.state), "🏷️ Tags")
        self.tabs.addTab(StorageTab(self.state), "📊 Storage")
        self.tabs.addTab(OldFilesTab(self.state), "🕒 Old Files")
        self.tabs.addTab(SearchTab(self.state), "🔎 Search")
        self.tabs.addTab(CleanupTab(self.state), "🧹 Cleanup")
        self.tabs.addTab(LeftoverTab(), "🗑️ Uninstall Cleaner")
        self.tabs.addTab(SecurityTab(), "🔒 Security")

        self.statusBar().showMessage("Ready — Smart File Manager v1.0")

    def choose_background(self):
        """Naya background image choose karo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Background Image Chuno", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if file_path:
            self.background_pixmap = QPixmap(file_path)
            self.save_settings(file_path)
            self.update()   # repaint trigger karo

    def clear_background(self):
        """Background hatao, default color pe wapas jao"""
        self.background_pixmap = None
        self.save_settings(None)
        self.update()

    def paintEvent(self, event):
        """Yeh Qt khud call karta hai jab bhi window repaint honi ho - yahan background draw karte hain"""
        painter = QPainter(self)
        if self.background_pixmap and not self.background_pixmap.isNull():
            scaled = self.background_pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # Center karke draw karo
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

            # Thoda dark overlay taaki text padhne mein aasani ho
            painter.fillRect(self.rect(), Qt.GlobalColor.black)
            painter.setOpacity(0.45)
            painter.fillRect(self.rect(), Qt.GlobalColor.black)
        super().paintEvent(event)