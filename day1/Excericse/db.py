

# ---------- CREATE FOLDER + FILE ----------
import json
import os

from config import DB_FOLDER, DB_PATH
_USERS = None  # private global state


def initialize_database():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({}, f)
#-------------Get users------------
def get_users():
    """Load users once and return the same instance everywhere"""
    global _USERS

    if _USERS is None:
        with open(DB_PATH, "r") as f:
            _USERS = json.load(f)

    return _USERS

# ---------- LOAD USERS ----------
def load_users():
    with open(DB_PATH, "r") as f:
        return json.load(f)


# ---------- SAVE USERS ----------
def save_users():
    global _USERS
    with open(DB_PATH, "w") as f:
        json.dump(_USERS, f, indent=4)