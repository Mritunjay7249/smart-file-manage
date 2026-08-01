import os


def get_folder_size(folder_path):
    """
    Ek folder ka TOTAL size deta hai (sab subfolders ki files milakar).
    Yeh recursion use karta hai - os.walk() folder ke andar khud hi jaata hai.
    """
    total_size = 0

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                total_size += os.path.getsize(file_path)
            except (OSError, FileNotFoundError):
                # Kabhi kabhi file access nahi hoti (permission issue), usse skip karo
                continue

    return total_size


def format_size(size_bytes):
    """Bytes ko KB/MB/GB mein badalta hai"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def analyze_storage(folder_path):
    """
    Diye gaye folder ke andar ke saare TOP-LEVEL items (files + subfolders)
    ka size nikaalta hai, aur sabse bade se chhote order mein dikhata hai.
    """

    if not os.path.exists(folder_path):
        print(f"Error: '{folder_path}' exist nahi karta.")
        return []

    items = os.listdir(folder_path)
    results = []  # yahan (naam, size, type) store hoga

    for item_name in items:
        item_path = os.path.join(folder_path, item_name)

        if os.path.isdir(item_path):
            size = get_folder_size(item_path)  # recursion yahan use ho raha hai
            item_type = "folder"
        else:
            try:
                size = os.path.getsize(item_path)
            except (OSError, FileNotFoundError):
                continue
            item_type = "file"

        results.append({
            "name": item_name,
            "size_bytes": size,
            "size_readable": format_size(size),
            "type": item_type,
        })

    # Sorting: sabse bada size sabse upar (reverse=True matlab descending order)
    results.sort(key=lambda item: item["size_bytes"], reverse=True)

    return results


def print_storage_report(folder_path):
    """Analysis ko sundar tarike se print karta hai"""
    results = analyze_storage(folder_path)

    if not results:
        print("Kuch nahi mila is folder mein.")
        return

    total = sum(item["size_bytes"] for item in results)

    print(f"\n--- Storage Report: {folder_path} ---")
    print(f"Total Size: {format_size(total)}\n")

    for item in results:
        icon = "[Folder]" if item["type"] == "folder" else "[File]  "
        print(f"{icon} {item['size_readable']:>10}   {item['name']}")