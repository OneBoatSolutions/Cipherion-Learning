#objectives
import os
import json

from util import simple_hash
from db import get_users, initialize_database, save_users

def login_user():
    users = get_users()
    mail_input = input("Enter your Mail Id : ")
    if mail_input not in users:
        print("Mail Id does not exist, please sign up.")
        signup_user()
        return
    for i in range (3):       
        pwd_input = input("Enter your Password: ")
        if users[mail_input]["password"] == simple_hash(pwd_input):

            print("Login successful!")
            return True, mail_input
        else:
            print("Invalid Password, try again")
            return False
    print("Too many attempts with incorrect password")           


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
    return True, mail_input




