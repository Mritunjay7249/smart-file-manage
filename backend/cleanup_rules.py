import sqlite3
import os
from datetime import datetime, timedelta
from backend.paths import DB_PATH


def init_rules_db():
    """Rules table banata hai (agar pehle se nahi hai)"""
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cleanup_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_path TEXT NOT NULL,
            extension TEXT,
            older_than_days INTEGER NOT NULL,
            action TEXT NOT NULL,
            enabled INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


def add_rule(folder_path, older_than_days, extension=None, action="delete"):
    """
    Naya cleanup rule banata hai.
    action: "delete" ya "notify" (abhi sirf yeh 2 support karenge)
    extension: None matlab sab file types pe apply hoga
    """
    init_rules_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cleanup_rules (folder_path, extension, older_than_days, action)
        VALUES (?, ?, ?, ?)
    """, (folder_path, extension, older_than_days, action))

    conn.commit()
    conn.close()

    print(f"Rule add ho gaya: '{folder_path}' mein {extension or 'saari'} files jo {older_than_days} din se purani hon, unpe action = {action}")


def get_all_rules():
    """Database se saare rules nikaalta hai"""
    init_rules_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, folder_path, extension, older_than_days, action, enabled FROM cleanup_rules")
    rows = cursor.fetchall()

    conn.close()

    rules = []
    for row in rows:
        rules.append({
            "id": row[0],
            "folder_path": row[1],
            "extension": row[2],
            "older_than_days": row[3],
            "action": row[4],
            "enabled": row[5],
        })

    return rules


def apply_rule(rule, dry_run=True):
    """
    Ek single rule ko apply karta hai.
    dry_run=True matlab abhi sirf DIKHAO kya hoga, actual delete mat karo.
    dry_run=False matlab ASLI mein delete karo.
    """
    folder_path = rule["folder_path"]

    if not os.path.exists(folder_path):
        print(f"Skip: '{folder_path}' exist nahi karta.")
        return

    cutoff_date = datetime.now() - timedelta(days=rule["older_than_days"])
    affected_files = []

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Extension filter (agar rule mein specify kiya gaya hai)
            if rule["extension"]:
                _, ext = os.path.splitext(file_name)
                if ext.lower() != rule["extension"].lower():
                    continue

            try:
                modified_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            except (OSError, FileNotFoundError):
                continue

            if modified_date < cutoff_date:
                affected_files.append(file_path)

    # Ab decide karo kya karna hai in files ke saath
    if dry_run:
        print(f"\n[DRY RUN] Rule ID {rule['id']}: {len(affected_files)} file(s) affect hongi:")
        for f in affected_files:
            print(f"   - {f}")
    else:
        for f in affected_files:
            if rule["action"] == "delete":
                try:
                    os.remove(f)
                    print(f"Deleted: {f}")
                except OSError as e:
                    print(f"Delete nahi ho paya: {f} — {e}")
            elif rule["action"] == "notify":
                print(f"Notify: '{f}' cleanup criteria pe fit baithti hai.")

    return affected_files


def apply_all_rules(dry_run=True):
    """Database ke saare ENABLED rules ko ek saath apply karta hai"""
    rules = get_all_rules()
    enabled_rules = [r for r in rules if r["enabled"] == 1]

    if not enabled_rules:
        print("Koi active rule nahi mila.")
        return

    for rule in enabled_rules:
        apply_rule(rule, dry_run=dry_run)