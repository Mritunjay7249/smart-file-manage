import os
import hashlib

def get_file_hash(file_path):
    """File ke content se ek unique fingerprint (hash) banata hai"""
    hasher = hashlib.md5()
    
    with open(file_path, "rb") as f:  # "rb" = read binary mode
        # Poori file ek saath memory mein nahi lete (bade files ke liye slow/crash ho sakta hai)
        # Isliye chhote-chhote chunks mein padhte hain
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    
    return hasher.hexdigest()  # hash ko readable string format mein return karo


def find_duplicates(folder_path):
    """Folder (aur uske subfolders) mein duplicate files dhundta hai"""
    
    if not os.path.exists(folder_path):
        print(f"Error: '{folder_path}' exist nahi karta.")
        return {}

    hash_map = {}  # { hash_value: [file_path1, file_path2, ...] }

    # os.walk() folder ke andar ke saare subfolders mein bhi jaata hai
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            try:
                file_hash = get_file_hash(file_path)
            except Exception as e:
                print(f"Skip kiya (padh nahi paya): {file_name} — {e}")
                continue

            if file_hash not in hash_map:
                hash_map[file_hash] = []

            hash_map[file_hash].append(file_path)

    # Ab sirf woh hashes chahiye jinke against 2 ya zyada files hain (matlab duplicates)
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}

    return duplicates


def print_duplicates(duplicates):
    """Duplicates ko sundar tarike se print karta hai"""
    if not duplicates:
        print("Koi duplicate file nahi mili.")
        return

    print(f"\n{len(duplicates)} duplicate group(s) mile:\n")
    
    for i, (file_hash, paths) in enumerate(duplicates.items(), start=1):
        print(f"Group {i}:")
        for path in paths:
            print(f"   - {path}")
        print()