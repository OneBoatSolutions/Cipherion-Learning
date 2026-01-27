#objectives
import os
import json

# ---------- CONFIG ----------
DB_FOLDER = "database"

DB_FILE = "users.json"
DB_PATH = os.path.join(DB_FOLDER, DB_FILE)

# ---------- CREATE FOLDER + FILE ----------
def initialize_database():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({}, f)


# ---------- LOAD USERS ----------
def load_users():
    with open(DB_PATH, "r") as f:
        return json.load(f)


# ---------- SAVE USERS ----------
def save_users(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)





def login_user(users):
    mail_input = input("Enter your Mail Id : ")
    if mail_input not in users:
        print("Mail Id does not exist, please sign up.")
        signup_user(users)
        return
    
    pwd_input = input("Enter your Password: ")
    if users[mail_input]["password"] == pwd_input:
        print("Login successful!")
    else:
        print("Invalid Password")



def signup_user(users ):

    mail_input = input("Enter your Mail ID: ")
    if mail_input in users:
        print("Mail Id already exists please login")
        login_user(users)
        return 

    username_input = input("Enter your Username : ")
    pwd_input = input("Enter your Password: ")
    data = {
        mail_input:{
                "username":username_input,
                "password": pwd_input
            }
        }
    users= load_users()
    users[mail_input]={
                "username":username_input,
                "password": pwd_input
            }
    save_users(users)

def main():

    print("Welcome to Tessent")
    print("1. Press 1 for login") 
    print("2. Press 2 for signup")
    initialize_database()
    users= load_users()
    while True:

        user_input = int(input("Enter your choice:"))
        if user_input == 1:
            login_user(users)
            break
        elif user_input == 2:
            signup_user(users)
            break
        else:
            print("Wrong choice, renter your choice")


main()
