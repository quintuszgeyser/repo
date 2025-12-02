# PLEASE ENSURE YOU OPEN THIS FILE IN  VS CODE.

# *** NOTE ON COMMENTS ***
# This is a comment in Python.
# Comments can be placed anywhere in Python code and the computer ignores them -- they are intended to be read by humans.
# Any line with a # in front of it is a comment.
# Please read all the comments in this example file and all others.


# ========= Another elif example ===========
# elif is short for else if.
# This allows you to specify a new condition to test, if the first condition is False.


# ************ Example 1 ************
num_str = input("Enter a number, or enter 'NO' to stop the program: ") 
if num_str == "2":
    num_int = int(num_str)
    # string input was cast to int
    print("The string '2' was successfully cast to an integer")
elif num_str == "3":
    num_int = int(num_str)
    # string input was cast to int 
    print("The string '3' was successfully cast to an integer")
else:
    print("The word 'NO' can't be cast to an int.")
    # Entering NO causes the print function to be executed.

# Entering anything other than 2, 3, or NO does not result in any output as no
# further options are not defined in the code.
# What happens if you enter a number other than 2 or 3? Can you adapt the program
# to output the text "I don't know what to do with this number for any number higher 
# than 3? Try it!
# Try entering 'no' rather than 'NO'. What happens? Why is Python's response not
# case sensitive in this case?
# Also try creating processing instructions for other input, and adding output for 
# every option.
