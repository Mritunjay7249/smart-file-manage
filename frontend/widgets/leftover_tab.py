from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt
from backend.leftover_finder import (
    find_leftovers, delete_leftover, find_temp_files,
    clean_temp_files, format_size
)


class LeftoverTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        outer = QVBoxLayout()
        self.setLayout(outer)
        outer.setContentsMargins(20, 20, 20, 20)

        sub_tabs = QTabWidget()
        outer.addWidget(sub_tabs)

        sub_tabs.addTab(self.build_leftover_section(), "App Leftovers")
        sub_tabs.addTab(self.build_temp_section(), "Temp Files")

    # ---------- Section 1: App Leftover Finder ----------

    def build_leftover_section(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        info = QLabel(
            "Kisi uninstall ki hui app ka naam likho — hum AppData, Program Files, "
            "Desktop, Start Menu mein uske leftover files dhundhenge."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(info)

        search_row = QHBoxLayout()
        self.app_name_input = QLineEdit()
        self.app_name_input.setPlaceholderText("jaise: Valorant, Discord, OldGame")
        search_row.addWidget(self.app_name_input)

        search_btn = QPushButton("🔍 Dhundo")
        search_btn.clicked.connect(self.run_leftover_search)
        search_row.addWidget(search_btn)
        layout.addLayout(search_row)

        self.leftover_tree = QTreeWidget()
        self.leftover_tree.setHeaderLabels(["Name", "Type", "Size", "Location", "Status"])
        self.leftover_tree.setColumnWidth(0, 200)
        self.leftover_tree.setColumnWidth(1, 60)
        self.leftover_tree.setColumnWidth(2, 80)
        self.leftover_tree.setColumnWidth(3, 350)
        layout.addWidget(self.leftover_tree)

        delete_btn = QPushButton("⚠ Selected Item Delete Karo")
        delete_btn.clicked.connect(self.delete_selected_leftover)
        layout.addWidget(delete_btn)

        self.leftover_status = QLabel("")
        self.leftover_status.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(self.leftover_status)

        return widget

    def run_leftover_search(self):
        self.leftover_tree.clear()
        app_name = self.app_name_input.text().strip()

        if not app_name:
            self.leftover_status.setText("Pehle app ka naam likho!")
            return

        results = find_leftovers(app_name)

        if not results:
            self.leftover_status.setText(f"'{app_name}' se koi leftover nahi mila.")
            return

        for item in results:
            size_str = format_size(item["size_bytes"])

            if item["is_protected"]:
                status = "⚠️ PROTECTED - mat delete karo"
            elif item["recently_used"]:
                status = f"⚠️ {item['days_old']} din pehle use hui"
            else:
                status = "Safe lagti hai"

            tree_item = QTreeWidgetItem([item["name"], item["type"], size_str, item["path"], status])

            if item["is_protected"]:
                for col in range(5):
                    tree_item.setForeground(col, Qt.GlobalColor.red)
            elif item["recently_used"]:
                for col in range(5):
                    tree_item.setForeground(col, Qt.GlobalColor.yellow)

            tree_item.setData(0, Qt.ItemDataRole.UserRole, item)
            self.leftover_tree.addTopLevelItem(tree_item)

        self.leftover_status.setText(f"{len(results)} item(s) mile.")

    def delete_selected_leftover(self):
        selected = self.leftover_tree.currentItem()
        if not selected:
            self.leftover_status.setText("Pehle list se ek item select karo.")
            return

        item_data = selected.data(0, Qt.ItemDataRole.UserRole)

        # Extra confirmation, especially agar protected/recent hai
        warning_text = f"'{item_data['name']}' ko permanently delete karna hai?"
        if item_data["is_protected"]:
            warning_text = f"⚠️ WARNING: Yeh system ke liye zaroori ho sakti hai!\n\n{warning_text}"
        elif item_data["recently_used"]:
            warning_text = f"⚠️ Yeh {item_data['days_old']} din pehle use hui thi.\n\n{warning_text}"

        confirm = QMessageBox.warning(
            self, "Confirm Delete", warning_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success, message = delete_leftover(item_data["path"])
            if success:
                self.leftover_status.setText(f"Deleted: {item_data['name']}")
                self.run_leftover_search()  # list refresh karo
            else:
                self.leftover_status.setText(f"Delete nahi hui: {message}")

    # ---------- Section 2: Temp File Cleaner ----------

    def build_temp_section(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        info = QLabel(
            "System ki temporary files (%TEMP%, Windows\\Temp) yahan dikhengi. "
            "Yeh files generally safe hoti hain delete karne ke liye. Jo file abhi "
            "use ho rahi hai (kisi open program dwara), woh automatically skip ho jayegi."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(info)

        scan_btn = QPushButton("🔍 Temp Files Scan Karo")
        scan_btn.clicked.connect(self.scan_temp_files)
        layout.addWidget(scan_btn)

        self.temp_tree = QTreeWidget()
        self.temp_tree.setHeaderLabels(["Name", "Size", "Days Old"])
        self.temp_tree.setColumnWidth(0, 400)
        self.temp_tree.setColumnWidth(1, 100)
        layout.addWidget(self.temp_tree)

        clean_btn = QPushButton("🧹 Saari Temp Files Clean Karo")
        clean_btn.clicked.connect(self.run_temp_clean)
        layout.addWidget(clean_btn)

        self.temp_status = QLabel("")
        self.temp_status.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(self.temp_status)

        return widget

    def scan_temp_files(self):
        self.temp_tree.clear()
        files = find_temp_files()

        total_size = 0
        for item in files:
            size_str = format_size(item["size_bytes"])
            tree_item = QTreeWidgetItem([item["name"], size_str, str(item["days_old"])])
            self.temp_tree.addTopLevelItem(tree_item)
            total_size += item["size_bytes"]

        self.temp_status.setText(f"{len(files)} item(s) mile — total {format_size(total_size)} space le rahe hain.")

    def run_temp_clean(self):
        confirm = QMessageBox.question(
            self, "Confirm", "Saari temp files delete karni hain?\n(Jo use ho rahi hongi, woh khud skip ho jayengi)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        result = clean_temp_files(min_days_old=0)
        freed = format_size(result["freed_bytes"])

        self.temp_status.setText(
            f"✅ {len(result['deleted'])} files delete hui, {freed} free hua. "
            f"({len(result['skipped'])} files skip hui, kyunki use ho rahi thi)"
        )
        self.scan_temp_files()  # list refresh