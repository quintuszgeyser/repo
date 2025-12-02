"""
Starting template for creating an email simulator program using
classes, methods, and functions.

This template provides a foundational structure to develop your own
email simulator. It includes placeholder functions and conditional statements
with 'pass' statements to prevent crashes due to missing logic.
Replace these 'pass' statements with your implementation once you've added
the required functionality to each conditional statement and function.

Note: Throughout the code, update comments to reflect the changes and logic
you implement for each function and method.
"""

# --- OOP Email Simulator --- #

# --- Email Class --- #
# Create the class, constructor and methods to create a new Email object.
class email:
    
    
    
    def __init__(self,email_address , subject_line ,email_content):
        self.email_address = email_address
        self.subject_line = subject_line
        self.email_content =  email_content
        self.has_been_read = False
        
        
    def mark_as_read(self):
        self.has_been_read = True
        
inbox = []


# Initialise the instance variables for each email.

# Create the 'mark_as_read()' method to change the 'has_been_read'
# instance variable for a specific object from False to True.


# --- Functions --- #
# Build out the required functions for your program.


def populate_inbox():
    # Create 3 sample emails and add them to the inbox list.
    inbox.append(email("alice@example.com", "Meeting Reminder", "Don't forget about the meeting at 3 PM today."))
    inbox.append(email("bob@example.net", "Project Update", "The project deadline has been moved to next Friday."))
    inbox.append(email("carol@example.org", "Lunch Invitation", "Would you like to join me for lunch tomorrow?"))
    

    
        


def list_emails():
    # Create a function that prints each email's subject line
    # alongside its corresponding index number,
    # regardless of whether the email has been read.
    for i, mail in enumerate(inbox):
        print(f"{i + 1}. {mail.subject_line}")
    


def read_email(index):
    # Create a function that displays the email_address, subject_line,
    # and email_content attributes for the selected email.
    # After displaying these details, use the 'mark_as_read()' method
    # to set its 'has_been_read' instance variable to True.
    mail = inbox[index]
    mail.mark_as_read()
    
    print(f"{mail} has been marked as read")
    
   

def view_unread_emails():
    # Create a function that displays all unread Email object subject lines
    # along with their corresponding index numbers.
    # The list of displayed emails should update as emails are read.
    pass


# --- Lists --- #
# Initialise an empty list outside the class to store the email objects.

# --- Email Program --- #

# Call the function to populate the inbox for further use in your program.
populate_inbox()
# Fill in the logic for the various menu operations.

# Display the menu options for each iteration of the loop.



while True:
    user_choice = int(
        input(
            """\nWould you like to:
    1. Read an email
    2. View unread emails
    3. Quit application

    Enter selection: """
        )
    )
  
    
    
    
    if user_choice == 1:
        # Add logic here to read an email
        
        list_emails() 
        choice = int(input("Choose a email number to read: "))
        read_email(choice-1)
        
    
        

    elif user_choice == 2:
        # Add logic here to view unread emails
       found_unread = False
       for i , mail in enumerate(inbox):
           if not mail.has_been_read:
                print(f"{i + 1}. {mail.subject_line}")
                found_unread = True
       if not found_unread:
            print("No unread emails.")

    elif user_choice == 3:
        # Add logic here to quit application.
        break

    else:
        print("Oops - incorrect input.")


