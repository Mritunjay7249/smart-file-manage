import os
import re
from datetime import datetime, timedelta


def search_files(folder_path, name_contains=None, extension=None,
                  min_size_kb=None, max_size_kb=None, modified_within_days=None):
    """
    Normal structured search - jitne bhi filters diye gaye hain, sab apply karta hai.
    Koi bhi filter None ho to woh ignore ho jaata hai.
    """

    if not os.path.exists(folder_path):
        print(f"Error: '{folder_path}' exist nahi karta.")
        return []

    results = []

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Filter 1: naam mein woh text hona chahiye
            if name_contains and name_contains.lower() not in file_name.lower():
                continue

            # Filter 2: extension match honi chahiye
            if extension:
                _, ext = os.path.splitext(file_name)
                if ext.lower() != extension.lower():
                    continue

            try:
                size_kb = os.path.getsize(file_path) / 1024
                modified_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            except (OSError, FileNotFoundError):
                continue

            # Filter 3: minimum size
            if min_size_kb is not None and size_kb < min_size_kb:
                continue

            # Filter 4: maximum size
            if max_size_kb is not None and size_kb > max_size_kb:
                continue

            # Filter 5: kitne din ke andar modify hui
            if modified_within_days is not None:
                cutoff = datetime.now() - timedelta(days=modified_within_days)
                if modified_date < cutoff:
                    continue

            # Agar file yahan tak pahunchi, matlab saare filters pass ho gaye
            results.append(file_path)

    return results


# ---------- Natural Language Search ----------

# Common file type names ko unke extensions se map karna
TYPE_KEYWORDS = {
    "pdf": [".pdf"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "photo": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "video": [".mp4", ".mkv", ".avi", ".mov"],
    "music": [".mp3", ".wav", ".flac"],
    "document": [".docx", ".doc", ".txt"],
    "text": [".txt"],
    "excel": [".xlsx"],
}

# Time-related phrases ko din ki sankhya mein badalna
TIME_KEYWORDS = {
    "today": 1,
    "aaj": 1,
    "this week": 7,
    "is hafte": 7,
    "last week": 14,
    "pichle hafte": 14,
    "this month": 30,
    "is mahine": 30,
    "last month": 60,
    "pichle mahine": 60,
    "6 months": 180,
    "6 mahine": 180,
}


def parse_natural_query(query):
    """
    User ki plain English/Hindi query ko padh kar, usme se
    extension aur time-range nikaalta hai.
    Example: "pichle mahine ki saari pdf files" -> {"extension": ".pdf", "days": 60}
    """
    query_lower = query.lower()

    parsed = {
        "extension": None,
        "days": None,
    }

    # File type dhundo
    for keyword, extensions in TYPE_KEYWORDS.items():
        if keyword in query_lower:
            parsed["extension"] = extensions[0]  # pehla extension le lo (jaise .pdf)
            break

    # Time phrase dhundo
    for phrase, days in TIME_KEYWORDS.items():
        if phrase in query_lower:
            parsed["days"] = days
            break

    return parsed


def natural_search(folder_path, query):
    """
    Natural language query lekar, use parse karke, phir search_files() ko call karta hai.
    """
    parsed = parse_natural_query(query)

    print(f"\nQuery samjhi: extension={parsed['extension']}, last {parsed['days']} din")

    results = search_files(
        folder_path,
        extension=parsed["extension"],
        modified_within_days=parsed["days"]
    )

    if not results:
        print("Koi file nahi mili is query se.")
    else:
        print(f"\n{len(results)} file(s) mili:")
        for path in results:
            print(f"   - {path}")

    return results
def advanced_search(folder_path, name_contains=None, extension=None,
                     min_size_kb=None, max_size_kb=None,
                     date_after=None, date_before=None):
    """
    Super search: sab filters ek saath, date range ke sath.
    date_after / date_before: datetime objects (ya None)
    """
    if not os.path.exists(folder_path):
        return []

    results = []

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            if name_contains and name_contains.lower() not in file_name.lower():
                continue

            if extension:
                _, ext = os.path.splitext(file_name)
                if ext.lower() != extension.lower():
                    continue

            try:
                size_kb = os.path.getsize(file_path) / 1024
                modified_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            except (OSError, FileNotFoundError):
                continue

            if min_size_kb is not None and size_kb < min_size_kb:
                continue
            if max_size_kb is not None and size_kb > max_size_kb:
                continue
            if date_after is not None and modified_date < date_after:
                continue
            if date_before is not None and modified_date > date_before:
                continue

            results.append({
                "path": file_path,
                "name": file_name,
                "size_kb": size_kb,
                "modified": modified_date,
            })

    return results
SKIP_FOLDERS = {
    "windows", "programdata", "$recycle.bin", "system volume information",
    "node_modules", ".git", "appdata", "$windows.~ws", "$windows.~bt",
    "msocache", "recovery",
}


def advanced_search_iter(folder_path, name_contains=None, extension=None,
                          min_size_kb=None, max_size_kb=None,
                          date_after=None, date_before=None,
                          stop_flag=None, skip_system=True):
    """
    Generator version - har match milte hi turant 'yield' kar deta hai,
    poora scan khatam hone ka wait nahi karta. Isse UI turant update ho sakti hai.
    stop_flag: ek [False] jaisi list, agar [True] ho jaye to turant rukna hai.
    """
    if not os.path.exists(folder_path):
        return

    for root, dirs, files in os.walk(folder_path):
        if stop_flag and stop_flag[0]:
            return

        if skip_system:
            # System folders ko dirs list se hi hata do, taaki os.walk unke andar jaaye hi na
            dirs[:] = [d for d in dirs if d.lower() not in SKIP_FOLDERS]

        for file_name in files:
            if stop_flag and stop_flag[0]:
                return

            if name_contains and name_contains.lower() not in file_name.lower():
                continue

            if extension:
                _, ext = os.path.splitext(file_name)
                if ext.lower() != extension.lower():
                    continue

            file_path = os.path.join(root, file_name)
            try:
                size_kb = os.path.getsize(file_path) / 1024
                modified_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            except (OSError, FileNotFoundError):
                continue

            if min_size_kb is not None and size_kb < min_size_kb:
                continue
            if max_size_kb is not None and size_kb > max_size_kb:
                continue
            if date_after is not None and modified_date < date_after:
                continue
            if date_before is not None and modified_date > date_before:
                continue

            yield {
                "path": file_path, "name": file_name,
                "size_kb": size_kb, "modified": modified_date,
            }