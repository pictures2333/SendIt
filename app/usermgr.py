from utils import dbhelper

# functions
def register():
    username = input("Enter username: ")
    password = input("Enter password: ")
    msg, err = dbhelper.solo_user_create(username, password)
    if err:
        print(msg)
        return
    print("Done!")


def delete():
    username = input("Enter username: ")
    err = dbhelper.solo_user_delete(username)
    if err:
        print("Failed!")
        return
    print("Done!")

# menu
print("[1] Register")
print("[2] Delete")
print("[9] Exit")

# action
choice=input("> ")
if choice == "1":
    register()
elif choice == "2":
    delete()
elif choice == "9":
    exit(0)
else:
    print("Invalid choice!")
