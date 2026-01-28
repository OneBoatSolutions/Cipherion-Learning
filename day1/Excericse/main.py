from auth import login_user, signup_user
from db import initialize_database
from chatbot import start_chat

def main():
    initialize_database()
    print("Welcome to Tessent")
    print("1. Press 1 for login") 
    print("2. Press 2 for signup")
    
    while True:
        user_input = int(input("Enter your choice:"))
        if user_input == 1:
            login_var, mail_input=login_user()
            if login_var ==True:
                start_chat(mail_input)
            break
        elif user_input == 2:
            login_var, mail_input=signup_user()
            if login_var ==True:
                start_chat(mail_input)
            break
        else:
            print("Wrong choice, renter your choice")

main()

