import os
from cryptography.fernet import Fernet
from backend.paths import KEY_PATH as KEY_FILE



def generate_key():
    """
    Ek naya encryption key banata hai aur file mein save karta hai.
    Yeh sirf EK BAAR chalana hai - baar baar chalane se purani encrypted files
    wapas decrypt nahi ho payengi (kyunki key badal jayegi).
    """
    os.makedirs("database", exist_ok=True)

    if os.path.exists(KEY_FILE):
        print("Key pehle se exist karti hai. Nayi key nahi banayi (safety ke liye).")
        return

    key = Fernet.generate_key()

    with open(KEY_FILE, "wb") as f:  # "wb" = write binary
        f.write(key)

    print(f"Nayi encryption key ban gayi: {KEY_FILE}")


def load_key():
    """Saved key ko file se wapas padhta hai"""
    if not os.path.exists(KEY_FILE):
        raise FileNotFoundError("Key nahi mili! Pehle generate_key() chalao.")

    with open(KEY_FILE, "rb") as f:  # "rb" = read binary
        return f.read()


def encrypt_file(file_path):
    """Ek file ko encrypt (lock) karta hai"""
    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' exist nahi karta.")
        return

    key = load_key()
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        original_data = f.read()

    encrypted_data = fernet.encrypt(original_data)

    # Original content ko encrypted content se replace kar do
    with open(file_path, "wb") as f:
        f.write(encrypted_data)

    print(f"Encrypted: {file_path}")


def decrypt_file(file_path):
    """Ek encrypted file ko wapas normal (unlock) karta hai"""
    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' exist nahi karta.")
        return

    key = load_key()
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        print(f"Decrypt nahi ho paya (galat key ya file corrupt hai): {e}")
        return

    with open(file_path, "wb") as f:
        f.write(decrypted_data)

    print(f"Decrypted: {file_path}")