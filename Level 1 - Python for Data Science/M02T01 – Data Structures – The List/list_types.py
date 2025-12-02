friends_names = ["Roelof","Wian","Schalk"]

print(friends_names[0])
print(friends_names[-1])
print(len(friends_names))


friends_ages = [24,23,28]

for i in range(0,len(friends_names)):
    print(str(friends_names[i]) +" is " + str(friends_ages[i]) +" years old")