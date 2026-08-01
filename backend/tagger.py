import sqlite3
import os
from backend.paths import DB_PATH


# Naam mein yeh keywords milein to yeh tag lagao
KEYWORD_TAGS = {
    "resume": ["resume", "cv"],
    "invoice": ["invoice", "bill", "receipt"],
    "screenshot": ["screenshot", "screen shot"],
    "report": ["report"],
    "photo": ["img", "photo", "pic"],
}


def init_db():
    """Database aur table banata hai (agar pehle se nahi hai to)"""
    os.makedirs("database", exist_ok=True)  # database folder na ho to bana do

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            tag TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def generate_tags(file_name):
    """File ke naam ke basis par tags suggest karta hai"""
    tags = []
    name_lower = file_name.lower()

    for tag, keywords in KEYWORD_TAGS.items():
        for keyword in keywords:
            if keyword in name_lower:
                tags.append(tag)
                break  # ek keyword mil gaya, isi tag ke doosre keywords check karne ki zarurat nahi

    # Extension ke basis par bhi ek tag daal do
    _, extension = os.path.splitext(file_name)
    if extension:
        tags.append(extension.replace(".", "") + "-file")

    if not tags:
        tags.append("uncategorized")

    return tags


def save_tags(file_path, tags):
    """Tags ko database mein save karta hai"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for tag in tags:
        cursor.execute(
            "INSERT INTO tags (file_path, tag) VALUES (?, ?)",
            (file_path, tag)
        )

    conn.commit()
    conn.close()


def tag_folder(folder_path):
    """Poore folder ki files ko scan karke tags generate aur save karta hai"""
    init_db()

    if not os.path.exists(folder_path):
        print(f"Error: '{folder_path}' exist nahi karta.")
        return

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        tags = generate_tags(file_name)
        save_tags(file_path, tags)
        print(f"{file_name} -> tags: {tags}")

    print(f"\nDone! {len(files)} files ko tag kiya gaya.")


def search_by_tag(tag):
    """Database mein ek tag se files dhundhta hai"""
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT file_path FROM tags WHERE tag = ?", (tag,))
    results = cursor.fetchall()  # list of tuples milegi, jaise [('path1',), ('path2',)]

    conn.close()

    if not results:
        print(f"'{tag}' tag wali koi file nahi mili.")
        return []

    print(f"\n'{tag}' tag wali files:")
    file_paths = []
    for row in results:
        print(f"   - {row[0]}")
        file_paths.append(row[0])

    return file_paths