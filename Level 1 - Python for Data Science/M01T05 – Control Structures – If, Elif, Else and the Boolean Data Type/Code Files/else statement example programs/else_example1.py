# PLEASE ENSURE YOU OPEN THIS FILE IN VSCode

# *** NOTE ON COMMENTS ***
# This is a comment in Python.
# Comments can be placed anywhere in Python code and the computer ignores them -- they are intended to be read by humans.
# Any line with a # in front of it is a comment.
# Please read all the comments in this example file and all others.


# ========= if-else Statements =========
# An if statement together with an else statement is known as an if-else statement
# The else statement represents an alternative path for the flow of logic if the condition of the if statement turns out to be False.
# If the if condition turns out to be True, the statements in the indented block following the if statement are executed.
# If the if condition turns out to be False, the statements in the indented block following the if statement are skipped,
# and the statements in the indented block following the else statement are executed.

# In Python, the general if-else syntax is:
# if condition :
#	indented Statements
# else:
#	indented Statements

#This is an example Python program demonstrating if-else statements.

name = input("Enter your name: \n")

if len(name) == 0:
    print("You didn't enter anything.")	
else:
    if len(name) > 10:
        print("You've got a long name.")

age = int(input("Thanks for entering your name. Enter your age: \n"))

print(name)
print(age)

# Run this program. Change your input to get different outputs due to the if statements.