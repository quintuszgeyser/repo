# PLEASE ENSURE YOU OPEN THIS FILE IN VSCode

# *** NOTE ON COMMENTS ***
# This is a comment in Python.
# Comments can be placed anywhere in Python code and the computer ignores them -- they are intended to be read by humans.
# Any line with a # in front of it is a comment.
# Please read all the comments in this example file and all others.


# =============  Writing if statements ==================
# if statements are a type of control structure which control the flow of logic within a program.
# if statements contain a condition.
# Conditions are statements that can only evaluate to a boolean value, True or False.
# If the condition is True then the indented statements are executed; if the condition is False then the indented statements are skipped.
# In Python, if statements have the following general syntax:
# if condition :
#     indented statements

#This is an example Python program demonstrating if statements.

name = input("Enter your name: \n")

if len(name) == 0:
	print("You didn't enter anything.")

if len(name) > 10:
	print("You've got a long name.")

print(name)

# Explanation:
# In the above example depending on the length of the users name a different message is displayed.

# Run this program. Change your input to get different outputs due to the if statements.



