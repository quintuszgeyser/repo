# =========== Dictionaries ===========

# =========== Creating a Dictionary ===========
# Dictionaries store key-value pairs enclosed in curly braces {}.
# Keys must be immutable (strings, numbers), values can be any data type.

# ************ Example 1 ************
print("\nExample 1:")

empty_dict = {}  # Empty dictionary

int_key_dict = {1: "apple", 2: "banana", 3: "orange"}  # Integer keys

string_key_dict = {
    "name": "John",
    "surname": "Doe",
    "gender": "male",
}  # String keys

mix_key_dict = {"word": "Python", 2: [1, 3, 4, 5]}  # Mixed keys

# =========== Accessing Elements from a Dictionary ===========
# Access values using keys in square brackets [] or with the get() method.

# ************ Example 2 ************
print("\nExample 2:")

profile_dict = {
    "name": "Chris",
    "surname": "Smith",
    "age": 28,
    "cell": "083 233 3242",
}

print(profile_dict["surname"])  # Accessing 'surname' using []
print(profile_dict.get("cell"))  # Accessing 'cell' using get()

# =========== Changing Elements in a Dictionary ===========
# Modify existing values or add new key-value pairs using assignment (=).

# ************ Example 3 ************
print("\nExample 3:")

profile_dict["age"] = 29  # Changing value for 'age'
print(profile_dict)

profile_dict["gender"] = "male"  # Adding new key-value pair
print(profile_dict)

# =========== Dictionary Membership Test ===========
# Check if a key exists in a dictionary using the 'in' keyword.

# ************ Example 4 ************
print("Example 4:")

doubles = {1: 2, 2: 4, 3: 6, 4: 8, 5: 10}

print(1 in doubles)  # True, '1' is a key in 'doubles'
print(8 in doubles)  # False, '8' is not a key in 'doubles'

# ****************** END OF EXAMPLE CODE ********************* #
