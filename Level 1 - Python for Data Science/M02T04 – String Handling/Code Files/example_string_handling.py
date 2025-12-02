# ========= Recap on Strings ===========
# A string is a common data type which is used to represent text.
# It is a sequence of characters, such as letters, numerals, symbols,
# and special characters.
# You have probably already noticed what an important part strings
# play in programming.
# Many programs you come across will involve the manipulation of strings.
# Therefore, knowing string manipulation techniques or string handling
# is crucial.

# ************ Example 1 ************
# Recap on slicing strings
print("Example 1: ")

string = "Hello world!"
fizz = string[0:5]

print(fizz)

# Note that slicing a string does not modify the original string.
# You can simply store the substring 'sliced' from the original string
# in a separate variable.
# By storing the substring in another variable, you keep
# the original string intact.

# ************ Example 2 ************
print("Example 2: ")

fact1 = "The original name of Windows was Interface Manager."

fact1 = fact1.upper()
print(fact1)

fact1 = fact1.lower()
print(fact1)

# Note that the value within 'fact1' is updated through the 'upper()'
# and 'lower()' methods as evident through the outputs.

# ************ Example 3 ************
print("Example 3: ")

# This an an example of a long string which is split over two lines.
sentence = (
    "ThisHELLOisHELLOrandomHELLOtextHELLOweHELLOareHELLO"
    "goingHELLOtoHELLOsplitHELLOapart"
)
split_sentence = sentence.split("HELLO")

print(split_sentence)

# Notice how a list is printed out? This is important to note as 
# the split() method will return a list of the split string.

# ************ Example 4 ************
print("Example 4: ")

# Original sentence with trailing whitespace on both ends
fact2 = (
    "     The$first$electronic$computer$ENIAC$weighed$more$than$27$tons.     "
)

# Replace '$' with 'WOW!'
fact2 = fact2.replace("$", "WOW!")
print(fact2)

# Remove leading and trailing whitespace
fact2 = fact2.strip()
print(fact2)

# Split the sentence into a list of words based on 'WOW!'
fact2 = fact2.split("WOW!")
print(fact2)

# Explanation:
# 1. The 'replace()' method replaces each '$' symbol with 'WOW!'.
# 2. The 'strip()' method removes leading and trailing whitespace.
# 3. The 'split()' method splits the sentence into a list based on 'WOW!'.
# This results in a list of words separated by 'WOW!'.

# ************ Example 5 ************
print("Example 5: ")

# Joining a list of strings into a single string with spaces in between
string_list = ["I", "like", "to", "join", "lists", "to", "make", "strings"]
list_joined = " ".join(string_list)
print(list_joined)

# Explanation:
# The '.join()' method concatenates elements of 'string_list'
# into a single string, inserting a space (' ') between each element.
# This creates a coherent sentence.

# ========= Escape Character ===========
# Python uses the backslash (\) as an escape character.
# The backslash (\) is used as a marker character to tell the
# compiler/interpreter that the next character has some special meaning.
# The backslash together with certain other characters
# are known as escape sequences.

# ************ Example 6 ************
print("\nExample 6: ")

# Using \n to create a line break in a string
people = "Person 1 \nPerson 2"
print(people)

# Notice the line break between the two words. The \n character is
# invisible as it's a command to insert a new line.

# Explanation:
# The '\n' escape sequence inserts a newline character,
# creating a line break in the output.

# ************ Example 7 ************
print("\nExample 7: ")

# Using \t to insert a tab space in a string
wage = "Person 1: \t 123.22"
print(wage)

# Notice the tab between the two words. The \t character is invisible
# as it's a command to insert a tab space.

# Explanation:
# The '\t' escape sequence inserts a tab character, aligning text
# after it as if it were in a table format.

# ************ Example 8 ************
print("\nExample 8: ")

# Using \\ to print a backslash in a string
sentence = (
    "The escape character (\\) is a character which invokes an alternative "
    "interpretation of subsequent characters in a character sequence."
)
print(sentence)

# Notice that the quotation marks and backslash are printed out
# as part of the string.

# Explanation:
# The '\\' escape sequence prints a single backslash character
# within a string, avoiding confusion with Python's interpretation
# of escape sequences.

# ****************** END OF EXAMPLE CODE ********************* #
