class Course:
    # Class attribute for the course name
    name = "Fundamentals of Computer Science"

    # Class attribute for the contact website
    contact_website = "www.hyperiondev.com"

    # Method to display contact details
    def contact_details(self):
        print("Please contact us by visiting", self.contact_website)
    
    def headofficeloc():
        print("Cape Town")
        
class OOPCourse(Course):
    def __init__(self):
        super().__init__()
        self.description = "OOP Fundamentals"
        self.trainer = "Mr Anon A. Mouse"
        self.course_id = "#12345"
    
    def trainer_details(self):
        print(f"The course is about { self.description} and is presented by: {self.trainer}  ")
        
    def show_course_id(self):
        print(self.course_id)

# Example usage:
# Create an instance of the Course class
course_1 = OOPCourse()


# Call the contact_details method to display contact information
course_1.contact_details()
course_1.trainer_details()
course_1.show_course_id()