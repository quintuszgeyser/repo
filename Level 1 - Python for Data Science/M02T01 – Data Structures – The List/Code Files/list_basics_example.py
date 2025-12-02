# ============= Creating a Lists ==================
# To create a list simply put different comma-separated values between square brackets.

# ************ Example 1 ************
# A List of Strings

string_list = ['John', 'Mary', 'Harry']
# Python knows that anything defined in [] is a list.
# There are 3 String items in this list.

# ************ Example 2 ************
# A List containing different datatypes

mixed_list = ['Hello', 3.4, 89, 'World']

# ************ Example 3 ************
# A List containing another List

my_list = ['Monkey', 'Elephant', [3, 4, 6, 10]]


# ============= Indexing Lists ==================
# We are able to access all elements in a list using the index operator [].
# The index starts from 0 for the leftmost item, so a list having 10 elements will have indices from 0 to 9.
# Alternatively the index can begin with -1 for the index of the rightmost item, so a list having 10 elements will have indices from -10 to -1.

# ************ Example 4 ************
print("Example 4: ")

pet_list = ['cat', 'dog', 'hamster', 'goldfish', 'parrot']

print(pet_list[0])
# Prints 'cat'.
# The element at position 0 is also known as the first element of a list, or the 'element at index 0'.

print(pet_list[-2])
# Prints 'goldfish'
# The element at position -2 is also known as the 4th element of the list, or the 'element at index -2'.


# ============= Slicing Lists ==================
# You can slice lists in the same way as you would slice strings.
# We can access a range of items in a list by using the slicing operator (colon).
# In order to slice a list you need to indicate a start and end position of the items you would like to access.
# You place these positions between the index operator [] and separate them with the colon.
# The item in the start position is included in the sliced list, while the item in the end position is not included.

# ************ Example 5 ************
print("\nExample 5: ")

num_list = [1, 4, 2, 7, 5, 9]

print(num_list[1:2])
# Prints everything from the 1st to the 2nd element of list, NOT including the 2nd element.
# So it only prints the item in the 1st position.

print(num_list[0:])
# Prints everything from the 0th position to the end of the list i.e. the entire list.

print(num_list)
# A faster way to print the entire list.


# ============= Changing Elements in a Lists ==================
# Elements in a list can be changed.
# You use the assignment operator (=) to change single or multiple elements.

# ************ Example 6 ************
print("\nExample 6:")

name_list = ['James', 'Molly', 'Chris', 'Peter', 'Kim']
name_list[2] = 'Tom'
# We can replace the 3rd element of the list with a new string.
# 'Chris' will be lost and replaced with 'Tom'.
print(name_list) # To see that the list has changed.

name_list[1:4] = ['Joe', 'Lucy', 'Kelly']
# We can replace the 2nd, 3rd and 4th elements of the list with a new string.
print(name_list) # To see that the list has changed.


# ============= Adding Elements to a Lists ==================
# You can add an element to the end of a list using the 'append()' method.

# ************ Example 7 ************
print("\nExample 7:")

newList = [34, 35, 75, 'Coffee', 98.8]
newList.append('Tea')
# Adds the String 'Tea' to the end of the list
print(newList)


# ============= Deleting Elements From a List ==================
# You can use the 'del' keyword to delete one or more items from a list.
# You are even able to delete the list entirely.

# ************ Example 8 ************
print("\nExample 8:")

charList = ['P', 'y', 't', 'h', 'o', 'n']

# Deletes the single element 'h'
del charList[3]
print(charList)

# Deletes multiple elements from the 2nd to 4th element.
del charList[1:3]
print(charList)

# Deletes the entire list
del charList


# ============= Getting the Length of a List ==================
# You can get the length of the list (how many elements there are in the list) by using the len() function.
# This is the same function we used to get the length of a string.

# ************ Example 9 ************
print("\nExample 9:")

oddNumList = [1, 3, 5, 7, 9]
print(len(oddNumList))
# Will print the total number of items in the list, currently 5.



# ================== Checking if Something is in a List ==================
# You can simply use an if statement to check if a certain item is in a list.


# ************ Example 10 ************
print("\nExample 10:")
groceryList = ['Bread', 'Milk', 'Butter', 'Cheese', 'Cereal']

if 'Apples' in groceryList:
        print('The item Apples was found in the list groceryList')
else:
        print('The item Apples was not found in the list groceryList')

# This is a much quicker way than looping through all the items, such as if you did:
for item in groceryList:
        if item == 'Apples':
                print('The item Apples was found in the list groceryList')



# ================== Using The range Function ==================
# The range function is a special Python function, that will automatically generate a list of integers within a specified range.

# ************ Example 11 ************
print("\nExample 11:")

num_till_10 = range(0, 10)
# This will create a list of integers =[0,1,2,3,4,5,6,7,9] and store it in the variable 'num_till_10'.

num_till_5 = range(0, 5)
# This will create a list of integers =[0,1,2,3,4] and store it in the variable 'num_till_5'.


num_2_till_5 = range(2, 5)
# This will create a list of integers =[2,3,4] and store it in the variable 'num_2_till_5'.


# The resulting list can be looped over like any list of integers, e.g., to print the numbers from 1 to 10:
for num in num_till_10:
        print(num)
print("\n")

# Since num_till_10 = range(0,10), the above for loop is exactly the same as:
for num in range(0, 10):
        print(num)



# ****************** END OF EXAMPLE CODE ********************* #

