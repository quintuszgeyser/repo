str_manip = input("Enter a sentence: ")

len_str_manip = len(str_manip) 
print(len_str_manip)

last = str_manip[len_str_manip-1:len_str_manip]

last_manip = str_manip.replace(last,'@')
print(last_manip)


print(str_manip[len_str_manip+1:len_str_manip-4:-1])



print(str_manip[0:3]+str_manip[len_str_manip-2:len_str_manip+1])