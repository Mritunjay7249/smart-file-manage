import sys
import os


def get_database_dir():
    """App ke database folder ka sahi path deta hai - exe ho ya normal python."""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(".")
    db_dir = os.path.join(base, "database")
    os.makedirs(db_dir, exist_ok=True)
    return db_dir


DB_PATH = os.path.join(get_database_dir(), "app_data.db")
KEY_PATH = os.path.join(get_database_dir(), "secret.key")