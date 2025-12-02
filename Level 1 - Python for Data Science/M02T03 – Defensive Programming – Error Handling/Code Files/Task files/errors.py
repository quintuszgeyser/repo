# This example program is meant to demonstrate errors.
 
# There are some errors in this program. Run the program, look at the error messages, and find and fix the errors.

print ("Welcome to the error program") #Syntax error no brackets was used
print() #syntax error indented incorrectly, logical error "\n" not nessasary for a new line 

# Variables declaring the user's age, casting the str to an int, and printing the result
age_Str = "24" #syntax error == should be used to say if something is equals to = is correct in this case to assighn a variable
age = int(age_Str) #syntax error indented  and runtime error , the sting part of age cannot be converted to int
print("I'm" + age_Str + "years old.") #runtime error age should be a string

# Variables declaring additional years and printing the total years of age
years_from_now = 3 #runtime error , this should be a integer
total_years = age + years_from_now

print("The total number of years:" + str(total_years)) #syntax error no brackets

# Variable to calculate the total number of months from the given number of years and printing the result

total_months = total_years * 12 + 6 #runtime error total is never defined , this should be total_years #logical error never added the 6 months
print ("In 3 years and 6 months, I'll be " + str(total_months) + " months old")  #syntax error no brackets

#HINT, 330 months is the correct answer

