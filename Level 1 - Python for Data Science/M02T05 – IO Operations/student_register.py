from pathlib import Path
num_students = int(input("Please enter the number of students: "))
n = 0
roaster = []
for i in range(0,num_students):
  student_id = input("Enter a student number: ")
  roaster.append(student_id)

file_path = Path("Level 1 - Python for Data Science") / "M02T05 – IO Operations" / "Code Files" / "Input" / "Task file" / "student_register.txt"

with open(file_path,"w+") as file:
  for line in roaster:
    file.write(line + f"\n")