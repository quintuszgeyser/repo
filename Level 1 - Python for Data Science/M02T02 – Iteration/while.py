import statistics
number = 1
numbers = []
while number != -1:
        
    number = int(input("Enter a number")) 
    if number == 0:
       print("0 is not a valid number!")
       continue
    else:
        numbers.append(number)
    
print(numbers[0:len(numbers)-1])
print(statistics.mean(numbers[0:len(numbers)-1]))
