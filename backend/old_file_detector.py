import os
from datetime import datetime, timedelta


def get_file_dates(file_path):
    """File ki modified aur accessed date nikaalta hai (readable format mein)"""
    
    modified_timestamp = os.path.getmtime(file_path)  # last edit kab hui
    accessed_timestamp = os.path.getatime(file_path)  # last kab kholi/use hui

    modified_date = datetime.fromtimestamp(modified_timestamp)
    accessed_date = datetime.fromtimestamp(accessed_timestamp)

    return modified_date, accessed_date


def find_old_files(folder_path, days_threshold=180):
    """
    Folder ki saari files check karta hai, aur woh files return karta hai
    jo 'days_threshold' se zyada din se access nahi hui (default: 180 din = ~6 mahine)
    """

    if not os.path.exists(folder_path):
        print(f"Error: '{folder_path}' exist nahi karta.")
        return []

    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    # cutoff_date matlab: "aaj se 180 din pehle ki date"
    # Agar file us se bhi purani access hui hai, matlab woh "old" hai

    old_files = []

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            try:
                _, accessed_date = get_file_dates(file_path)
            except (OSError, FileNotFoundError):
                continue

            if accessed_date < cutoff_date:
                days_old = (datetime.now() - accessed_date).days

                old_files.append({
                    "path": file_path,
                    "last_accessed": accessed_date.strftime("%Y-%m-%d"),
                    "days_since_access": days_old,
                })

    # Sabse purani file sabse upar dikhao
    old_files.sort(key=lambda item: item["days_since_access"], reverse=True)

    return old_files


def print_old_files_report(folder_path, days_threshold=180):
    """Old files ka report print karta hai"""
    old_files = find_old_files(folder_path, days_threshold)

    if not old_files:
        print(f"\nKoi bhi file {days_threshold} din se purani access nahi hui. Sab kuch recent hai.")
        return

    print(f"\n--- {len(old_files)} file(s) mili jo {days_threshold}+ din se access nahi hui ---\n")

    for item in old_files:
        print(f"   {item['days_since_access']:>4} din pehle   |   {item['last_accessed']}   |   {item['path']}")