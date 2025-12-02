import re
from pathlib import Path

file_path = Path("Level 1 - Python for Data Science") / "M02T05 – IO Operations" / "Code Files" / "Input" / "Task file" / "DOB.txt"
with open(file_path,'r') as file:
    lines = file.readlines()

print("Name")
for line in lines:
  num_index = re.search(r"[0-9]",line).span()
  print(line[0:num_index[0]])


print(f"\nBirthdate")
for line in lines:
  if line != lines[-1]:
    num_index = re.search(r"[0-9]",line).span()
    print(line[num_index[0]:len(line)-1])
  else:
   print(line[num_index[1]:len(line)])
  
