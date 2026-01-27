import json
import os

DB_FOLDER = "database"
DB_FILE = "users.json"
DB_PATH = os.path.join(DB_FOLDER, DB_FILE)


def simple_hash(password):
    hash_value = 0
    prime = 31
    for char in password:
        hash_value = (hash_value * prime + ord(char)) % 100000
    return str(hash_value)


def migrate_passwords():
    with open(DB_PATH, "r") as f:
        users = json.load(f)

    for email, data in users.items():
        plain_password = data["password"]

        # hash only if not already hashed
        if not plain_password.isdigit():
            continue

        hashed_password = simple_hash(plain_password)
        users[email]["password"] = hashed_password

    with open(DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

    print(" Password migration completed successfully")


if __name__ == "__main__":
    migrate_passwords()

