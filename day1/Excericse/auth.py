#objectives
import os
import json

# ---------- CONFIG ----------
DB_FOLDER = "database"

DB_FILE = "users.json"
DB_PATH = os.path.join(DB_FOLDER, DB_FILE)
_USERS = None  # private global state


# ---------- CREATE FOLDER + FILE ----------
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
#-------------------HASH--------------
def simple_hash(password):
    hash_value = 0
    prime = 31
    for char in password:
        hash_value = (hash_value * prime + ord(char)) % 100000
    return str(hash_value)




def login_user():
    users = get_users()
    mail_input = input("Enter your Mail Id : ")
    if mail_input not in users:
        print("Mail Id does not exist, please sign up.")
        signup_user()
        return
    
    pwd_input = input("Enter your Password: ")
    if users[mail_input]["password"] == simple_hash(pwd_input):

        print("Login successful!")
    else:
        print("Invalid Password")



def signup_user():
    users = get_users()


    mail_input = input("Enter your Mail ID: ")
    if mail_input in users:
        print("Mail Id already exists please login")
        login_user(users)
        return 

    username_input = input("Enter your Username : ")
    pwd_input = input("Enter your Password: ")

    users[mail_input] = {
        "username": username_input,
        "password": simple_hash(pwd_input)
    }
  
    save_users()
    print("Signup successful!")



def main():
    initialize_database()
    print("Welcome to Tessent")
    print("1. Press 1 for login") 
    print("2. Press 2 for signup")
    
    while True:

        user_input = int(input("Enter your choice:"))
        if user_input == 1:
            login_user()
            break
        elif user_input == 2:
            signup_user()
            break
        else:
            print("Wrong choice, renter your choice")


main()
