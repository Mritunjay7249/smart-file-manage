import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.organizer import organize_folder


class FileChangeHandler(FileSystemEventHandler):
    """
    Yeh class batati hai ki jab bhi folder mein kuch badle
    (file aaye, delete ho, rename ho), to kya karna hai.
    watchdog library ise "event handler" kehti hai.
    """

    def __init__(self, folder_path, auto_organize=False):
        self.folder_path = folder_path
        self.auto_organize = auto_organize

    def on_created(self, event):
        """Jab bhi koi NAYI file/folder banti hai, yeh function apne aap call hota hai"""
        if event.is_directory:
            return  # naye subfolders ko ignore karo, sirf files pe react karo

        print(f"[NEW FILE] {event.src_path}")

        if self.auto_organize:
            print("   -> Auto-organizing folder...")
            organize_folder(self.folder_path)

    def on_deleted(self, event):
        """Jab koi file delete hoti hai"""
        if event.is_directory:
            return
        print(f"[DELETED] {event.src_path}")

    def on_modified(self, event):
        """Jab koi file edit/modify hoti hai"""
        if event.is_directory:
            return
        print(f"[MODIFIED] {event.src_path}")


def start_watching(folder_path, auto_organize=False):
    """
    Diye gaye folder ko continuously monitor karta hai.
    Jab tak program band nahi karoge (Ctrl+C), yeh chalta rahega.
    """
    event_handler = FileChangeHandler(folder_path, auto_organize=auto_organize)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    # recursive=False matlab sirf isi folder ko dekho, subfolders ko nahi

    observer.start()
    print(f"Watching: {folder_path}")
    print("Rukne ke liye Ctrl+C dabao...\n")

    try:
        while True:
            time.sleep(1)  # har 1 second wait karo, CPU zyada use na ho
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatching band ho gayi.")

    observer.join()