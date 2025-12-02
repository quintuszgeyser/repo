word = input("Please enter a string: ")
string = ""


for i in range(0,len(word)):
    if i%2 == 0:
        
        string += word[i].upper()
    else:
        
        string += word[i].lower()


print(string)


split_words = word.split()

for i in range(0,len(split_words)):
    if i%2 == 0:
       
        split_words[i] = split_words[i].lower()
    else:
       
        split_words[i] = split_words[i].upper()

print(" ".join(split_words))
