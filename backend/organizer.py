import os
import shutil

# Har file extension kis folder mein jayegi, yeh mapping
FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Music": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar"],
}

def get_category(file_extension):
    """Extension dekh kar batata hai yeh file kis category mein jayegi"""
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension.lower() in extensions:
            return category
    return "Others"  # agar kisi list mein na mile

def organize_folder(folder_path):
    """Diye gaye folder ki saari files ko category-wise subfolder mein daal deta hai"""
    
    if not os.path.exists(folder_path):
        print(f"Error: '{folder_path}' naam ka folder exist nahi karta.")
        return

    # Folder ke andar ki saari cheezein list karo
    items = os.listdir(folder_path)

    moved_count = 0

    for item_name in items:
        item_path = os.path.join(folder_path, item_name)

        # Agar yeh ek folder hai, to usse skip karo (sirf files organize karni hain)
        if os.path.isdir(item_path):
            continue

        # File ka extension nikaalo (jaise "photo.jpg" se ".jpg")
        _, extension = os.path.splitext(item_name)

        category = get_category(extension)

        # Category ke naam ka subfolder banao (agar pehle se nahi hai)
        category_folder = os.path.join(folder_path, category)
        os.makedirs(category_folder, exist_ok=True)

        # File ko us subfolder mein move karo
        destination = os.path.join(category_folder, item_name)
        shutil.move(item_path, destination)

        print(f"Moved: {item_name} -> {category}/")
        moved_count += 1

    print(f"\nDone! Total {moved_count} files organize ho gayi.")