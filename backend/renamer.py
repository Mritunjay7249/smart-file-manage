import os

def bulk_rename(folder_path, prefix, start_number=1):
    """
    Folder ki saari files ko naye pattern se rename karta hai.
    Example: prefix="Holiday" -> Holiday_1.jpg, Holiday_2.jpg, ...
    """
    
    if not os.path.exists(folder_path):
        print(f"Error: '{folder_path}' exist nahi karta.")
        return

    # Sirf files lo, folders skip karo
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    if not files:
        print("Is folder mein koi file nahi mili.")
        return

    counter = start_number

    for file_name in files:
        old_path = os.path.join(folder_path, file_name)

        # Original extension nikaalo (jaise ".jpg"), taaki naya naam bhi same type ka rahe
        _, extension = os.path.splitext(file_name)

        new_name = f"{prefix}_{counter}{extension}"
        new_path = os.path.join(folder_path, new_name)

        # Agar yeh naam pehle se kisi file ka hai, to skip karo (safety check)
        if os.path.exists(new_path):
            print(f"Skip kiya (naam pehle se hai): {new_name}")
            counter += 1
            continue

        os.rename(old_path, new_path)
        print(f"Renamed: {file_name} -> {new_name}")

        counter += 1

    print(f"\nDone! {len(files)} files rename ho gayi.")


def preview_rename(folder_path, prefix, start_number=1):
    """
    ASLI rename karne se PEHLE, dikhata hai ki naye naam kya honge.
    Yeh professional apps mein common feature hai - user ko pehle dikhao, phir confirm lo.
    """
    if not os.path.exists(folder_path):
        print(f"Error: '{folder_path}' exist nahi karta.")
        return

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    counter = start_number
    print("Preview (abhi kuch rename nahi hua):\n")

    for file_name in files:
        _, extension = os.path.splitext(file_name)
        new_name = f"{prefix}_{counter}{extension}"
        print(f"   {file_name}  ->  {new_name}")
        counter += 1