"""
Student Management Program

This program defines the Student class for managing student data and
computing average grades.
"""


class Student:
    """
    A class representing a student.

    Attributes:
        age (int): The age of the student.
        name (str): The name of the student.
        gender (str): The gender of the student.
        grades (list of int): List of grades obtained by the student.

    Methods:
        __init__(age, name, gender, grades):
            Initializes a new student instance.

        compute_average():
            Computes and prints the average grade of the student.
    """

    # Constructor method
    def __init__(self, age, name, gender, grades):
        """Initializes a new student instance."""
        self.age = age
        self.name = name
        self.gender = gender
        self.grades = grades

    #  Method to calculate average grade
    def compute_average(self):
        """Computes and prints the average grade of the student."""
        average = sum(self.grades) / len(self.grades)
        print("The average for student " + self.name + " is " + str(average))


# Create Student objects.
philani = Student(20, "Philani Sithole", "Male", [64, 65])
sarah = Student(19, "Sarah Jones", "Female", [82, 58])

# Using dot notation to call 'compute_average()' method.
sarah.compute_average()

# Try to create a new Student object to test your understanding.
