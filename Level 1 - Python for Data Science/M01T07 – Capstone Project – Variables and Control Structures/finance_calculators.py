import math  

# printing menu options for the user to choose from
print("Investment - to calculate the amount of interest you'll earn on your investment.")
print("Bond - to calculate the amount you'll have to pay on a home loan.")
print()

# ask user which type of calculation they want to do and make it uppercase for easy comparison
calctype = input("Enter either 'investment' or 'bond' from the menu above to proceed:").upper()

# check if the user chose "investment"
if calctype == "Investment".upper():
    
    
    try:
        amount = float(input("Please enter the amount of money to invest: "))  
        interest_rate = float(input("Enter the interest rate: "))  
        num_years = int(input("Number of years to be invested: ")) 
        
    except ValueError:
         print("Invalid input! Please enter numeric values only.")
         exit()

    interest = input("Simple or Compound interest? ").upper() 

    # if the user chooses simple interest
    if interest == "simple".upper():
       fv = amount*(1+interest_rate/100*num_years)  
       print("You will recieve R"+str(round(fv,2))) 
       
    # if the user chooses compound interest
    elif interest == "Compound".upper():
        fv = amount*math.pow((1+interest_rate/100),num_years)  
        print("You will recieve R"+str(round(fv,2)))  

    # if the user entered something invalid
    else:
        print("not a valid response")

# check if the user chose "bond"
elif  calctype == "Bond".upper():
    try:
     pv = float(input("Please enter the present value of the house: "))  
     mon_interest_rate = (float(input("Enter the interest rate: "))/100)/12  
     num_months_to_repay = int(input("Number of months to repay: "))  
    
    except ValueError:
        print("Invalid input! Please enter numeric values only.")
        exit()  

    # bond repayment formula to calculate monthly payment
    repayment = (mon_interest_rate * pv) / (1 - math.pow((1 + mon_interest_rate), -num_months_to_repay))

    print("Your montly repayment will be R"+str(round(repayment,2)))  

# if the user entered something other than investment or bond
else:   
    print("not a valid response!")
