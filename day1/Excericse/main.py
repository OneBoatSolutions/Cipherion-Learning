from auth import login_user, signup_user
from db import initialize_database

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