import os
import shutil
from datetime import datetime

# Yeh jagah hain jahan uninstaller apna kachra chhod jaate hain
COMMON_LOCATIONS = [
    os.path.expandvars(r"%APPDATA%"),
    os.path.expandvars(r"%LOCALAPPDATA%"),
    os.path.expandvars(r"%PROGRAMDATA%"),
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    os.path.join(os.path.expanduser("~"), "Desktop"),
    os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
]

# System-critical folders - inhe kabhi bhi delete suggest nahi karenge, chahe naam match ho
PROTECTED_KEYWORDS = [
    "windows", "microsoft", "system32", "drivers", "nvidia", "intel",
    "realtek", "directx", "dotnet", "vcredist", ".net", "common files",
    "winsxs", "wininit",
]


def find_leftovers(app_name):
    """
    App ka naam lekar, common jagahon mein us naam se milte-julte
    files/folders dhundhta hai.
    """
    app_name_lower = app_name.lower().strip()
    if not app_name_lower:
        return []

    results = []

    for base_path in COMMON_LOCATIONS:
        if not os.path.exists(base_path):
            continue

        try:
            items = os.listdir(base_path)
        except (PermissionError, OSError):
            continue

        for item_name in items:
            item_lower = item_name.lower()

            if app_name_lower not in item_lower:
                continue

            full_path = os.path.join(base_path, item_name)

            # Safety check: kya yeh protected/system related hai?
            is_protected = any(keyword in item_lower for keyword in PROTECTED_KEYWORDS)

            try:
                if os.path.isdir(full_path):
                    size = get_folder_size(full_path)
                    item_type = "folder"
                else:
                    size = os.path.getsize(full_path)
                    item_type = "file"
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
            except (OSError, PermissionError):
                continue

            # Recent use check - agar 7 din ke andar use hui hai, warning do
            days_old = (datetime.now() - modified).days
            recently_used = days_old < 7

            results.append({
                "path": full_path,
                "name": item_name,
                "type": item_type,
                "size_bytes": size,
                "is_protected": is_protected,
                "recently_used": recently_used,
                "days_old": days_old,
            })

    return results


def get_folder_size(folder_path):
    total = 0
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except (OSError, FileNotFoundError):
                continue
    return total


def delete_leftover(path):
    """Ek leftover item delete karta hai (file ya poora folder)"""
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True, "Deleted"
    except Exception as e:
        return False, str(e)


# ---------- Temp File Cleaner ----------

TEMP_LOCATIONS = [
    os.path.expandvars(r"%TEMP%"),
    os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
    r"C:\Windows\Temp",
]


def find_temp_files():
    """System ki temp files dhundhta hai jo safely delete ho sakti hain"""
    results = []

    for temp_path in TEMP_LOCATIONS:
        if not os.path.exists(temp_path):
            continue

        try:
            items = os.listdir(temp_path)
        except (PermissionError, OSError):
            continue

        for item_name in items:
            full_path = os.path.join(temp_path, item_name)
            try:
                if os.path.isdir(full_path):
                    size = get_folder_size(full_path)
                else:
                    size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
            except (OSError, PermissionError):
                continue

            days_old = (datetime.now() - modified).days

            results.append({
                "path": full_path,
                "name": item_name,
                "size_bytes": size,
                "days_old": days_old,
                "in_use": False,   # agar delete fail hui, matlab file currently use ho rahi hai
            })

    results.sort(key=lambda x: x["size_bytes"], reverse=True)
    return results


def clean_temp_files(min_days_old=0):
    """
    Temp files delete karta hai. min_days_old se purani hi delete hongi
    (0 = sab, chahe abhi ki bhi ho).
    Jo files 'in use' hongi (locked by running program), unhe skip kar dega,
    crash nahi hoga.
    """
    files = find_temp_files()
    deleted = []
    skipped = []
    freed_bytes = 0

    for item in files:
        if item["days_old"] < min_days_old:
            continue

        try:
            if os.path.isdir(item["path"]):
                shutil.rmtree(item["path"])
            else:
                os.remove(item["path"])
            deleted.append(item["name"])
            freed_bytes += item["size_bytes"]
        except Exception:
            # File currently use ho rahi hai ya permission nahi hai - skip karo, crash mat ho
            skipped.append(item["name"])

    return {"deleted": deleted, "skipped": skipped, "freed_bytes": freed_bytes}


def format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"