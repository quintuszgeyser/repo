# =========== Write Method ===========
# You can use the write() method in order to write to a file.
# The syntax for this method is as follows:
#   file.write("string")   - writes "string" to the file

# ************ Example ************
# Before you can write to a file you need to open it.
# You open a file using Python's built-in open() function which
# creates a file called output.txt (it doesn't exist yet) in write mode.
# Python will automatically create this file in the same directory/folder
# that our program is in.

# Storing the user's name
name = input("Enter your name: ")

# Using 'with open' ensures automatic file closure
with open("output.txt", "w") as output_file:
    # Writes 'name' followed by a newline to output file
    output_file.write(name + "\n")

    # Writes additional content to the file on a new line.
    output_file.write("My name is on the line above in this text file.\n")

    # Note that the newline character (\n) is added at the end of the string
    # to ensure that each line is written on a new line within the text file.
    # Experimenting with the placement of the newline character
    # to observe how it affects where the new data is written
    # in the text file.

# Keep in mind that the file is automatically closed by the
# 'with' statement context manager.

# ****************** END OF EXAMPLE CODE ********************* #
