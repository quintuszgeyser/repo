# =========== Python list Methods  ===========
# There are many useful built-in list methods available for you to use.
# Some other list methods can be found below:
#   extend()    - Adds all elements of a list to the another list
#   insert()    - Inserts an item at the defined index
#   remove()    - Removes an item from the list
#   pop()       - Removes and returns an element at the given index
#   index()     - Returns the index of the first matched item
#   count()     - Returns the count of number of items passed as an argument
#   sort()      - Sorts items in a list in ascending order
#   reverse()   - Reverses the order of items in the list

# =========== The Copy Module  ===========
# Let's take a closer look at the copy module.
# There are several ways to make a copy of a list.
# The simplest way to make a copy is to use the copy() method.
# Using the copy() method ensures that if you modify the copied list,
# the original list remains the same.
# However, if your list contains other lists as items, those inner lists in
# the original list can still be modified
# if the corresponding inner list in the copied list is modified.
# This is called a shallow copy.
# Slicing lists also creates a shallow copy of a list.
# Therefore, when the list contains other lists as items, the inner lists
# have to be copied as well.
# You could do this manually but Python already contains a method to do it,
# the deepcopy() method.
# In order to use the deepcopy() and copy() methods you must import the
# copy module.

# ************ Example 1 ************
print("Example 1:")

import copy  # Imports are typically placed at the top of the file.

a = [[1, 2, 3], [4, 5, 6]]
b = copy.copy(a)  # Shallow copy using copy.copy()
c = a[:]  # Shallow copy using slicing
d = copy.deepcopy(a)  # Deep copy using copy.deepcopy()

b[1][0] = 10
c[1][1] = 11
d[1][2] = 12

print("List a:")
print(a)
print("List b:")
print(b)
print("List c:")
print(c)
print("List d:")
print(d)  # Only d[1][2] is changed due to deep copy

# ================== Looping Over Lists ==================
# What if you have a list of items and you want to do something to each item?
# You simply use a for loop to loop over every item in the list.

# ************ Example 2 ************
print("\nExample 2:")

food_list = [
    "Pizza",
    "Burger",
    "Fries",
    "Pasta",
    "Salad",
]  # Define a list of strings

for food in food_list:
    print(food)
# This loop prints out every item in the list.
# This is a very powerful tool in Python and shows how you can simply loop
# through a list.

# ************ Example 3 ************
print("\nExample 3:")

numbers = [1, 2, 3, 4]

for num in numbers:
    print(num)

# Any type of list can be looped over using this construct.
# The above will print out the numbers 1 to 4 - i.e. the entries
# in the list 'numbers'.


# =========== List Comprehension ===========
# List comprehension offers an elegant way to create lists based on
# existing lists.
# It applies an operation to each element and collects results in a new list.

# ************ Example 4 ************
print("\nExample 4:")

num_list = ["1", "5", "8", "14", "25", "31"]
print(num_list)

# Convert string elements to integers using list comprehension
new_num_list_ints = [int(element) for element in num_list]
print(new_num_list_ints)  # Prints converted integers

# Sum of integers in new_num_list_ints using built-in sum() function as
# new_num_list_ints now contains integer elements instead of string elements.
print(sum(new_num_list_ints))  # Output: 84

# ************ Example 5 ************
# You can do many operations with list comprehensions.
print("\nExample 5:")

# Create a new list where each element in new_num_list_ints is doubled
double_list = [2 * element for element in new_num_list_ints]
print(double_list)

# Create a new list where each element in new_num_list_ints is halved
half_list = [0.5 * element for element in new_num_list_ints]
print(half_list)



# ****************** END OF EXAMPLE CODE ********************* #
