import statistics

numbers = []
print("Please enter 10 numbers, integer or float")
for i in range(1,11):
    user_number = float(input("Enter number "+ str(i) +": "))
    numbers.append(user_number) 

print("Total:"+str(sum(numbers)))

max_val = max(numbers)
print("Maximum number index:"+str(numbers.index(max_val)))

min_val = min(numbers)
print("Minimum number index:"+str(numbers.index(min_val)))

round_avg = round(statistics.mean(numbers),2)

print("rounded average: "+str(round_avg))

med = statistics.median(numbers)

print("Median: "+ str(med))