import os

# Kaunse extensions ko "text" maana jaaye (inka content seedha padh sakte hain)
TEXT_EXTENSIONS = [".txt", ".py", ".md", ".csv", ".json", ".log"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]


def get_file_info(file_path):
    """File ki basic details deta hai - size, type, last modified"""
    
    if not os.path.exists(file_path):
        return {"error": f"'{file_path}' exist nahi karta."}

    size_bytes = os.path.getsize(file_path)
    size_readable = format_size(size_bytes)

    modified_time = os.path.getmtime(file_path)  # yeh ek number (timestamp) deta hai

    _, extension = os.path.splitext(file_path)

    return {
        "name": os.path.basename(file_path),
        "extension": extension,
        "size": size_readable,
        "modified_timestamp": modified_time,
    }


def format_size(size_bytes):
    """Bytes ko readable format mein badalta hai (KB, MB, GB)"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def preview_file(file_path, max_chars=500):
    """
    File ka preview deta hai:
    - Text file ho to content ka ek hissa
    - Image ho to sirf info (abhi actual image nahi dikha sakte, terminal mein)
    - Baaki files ke liye sirf basic info
    """
    
    info = get_file_info(file_path)
    
    if "error" in info:
        print(info["error"])
        return

    extension = info["extension"].lower()

    print(f"\n--- Preview: {info['name']} ---")
    print(f"Size: {info['size']}")

    if extension in TEXT_EXTENSIONS:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(max_chars)
            print(f"Content (pehle {max_chars} characters):\n")
            print(content)
        except Exception as e:
            print(f"Content padh nahi paya: {e}")

    elif extension in IMAGE_EXTENSIONS:
        print("Yeh ek image file hai. (GUI banne ke baad yahan actual image dikhengi)")

    else:
        print("Iss file type ka preview abhi support nahi hai, sirf info dikhayi.")

    print("--- End Preview ---\n")