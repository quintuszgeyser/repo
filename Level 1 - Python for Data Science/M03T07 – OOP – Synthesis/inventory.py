

from pathlib import Path
from tabulate import tabulate

file_path = Path("inventory.txt")

headers = ["country", "code", "product", "cost", "quantity"]
#========The beginning of the class==========
class Shoe:

    def __init__(self, country, code, product, cost, quantity):   
        '''
            In this function, you must initialise the following attributes:
            ● country,
            ● code,
            ● product,
            ● cost, and
            ● quantity.
        '''
        self.country =country
        self.code =code
        self.product =product
        self.cost =cost
        self.quantity = quantity
        
       
     
    def get_cost(self):
        pass
        '''
        Add the code to return the cost of the shoe in this method.
        '''
        return(self.cost)

    def get_quantity(self):
        pass
        '''
        Add the code to return the quantity of the shoes.
        '''
        return(self.quantity)
        

    def __str__(self):
        pass
        '''
        Add a code to returns a string representation of a class.
        '''
        return f"{self.country} ,{self.code} , {self.product}, {self.cost}, {self.quantity}"


#=============Shoe list===========
'''
The list will be used to store a list of objects of shoes.
'''
shoe_list = []


#==========Functions outside the class==============
def read_shoes_data():
    if not file_path.exists():
        
        with open(file_path, "w") as file:
            file.write("Country,Code,Product,Cost,Quantity\n")
        print(f"{file_path} not found. A new file has been created.")
        return shoe_list

    try:
        with open(file_path, "r") as file:
            next(file) 
            for line in file:
                temp = line.strip().split(",")
                shoe_list.append(Shoe(temp[0], temp[1], temp[2], float(temp[3]), int(temp[4])))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return shoe_list


    
def capture_shoes():
    country = input("Insert Country: ")
    code = input("Insert Code: ")
    product = input("Insert Product: ")
    cost = float(input("Insert Cost: "))
    quantity = int(input("Insert Quantity: "))    

    new_shoe = Shoe(country, code, product, cost, quantity)
    shoe_list.append(new_shoe)
    
    # Append the new shoe to inventory.txt
    with open(file_path, "a") as file:
        file.write(f"{country},{code},{product},{cost},{quantity}\n")
    
    print(f"{product} has been added successfully.")
    return shoe_list

    
    

def view_all():
    pass
    '''
    This function will iterate over the shoes list and
    print the details of the shoes returned from the __str__
    function. Optional: you can organise your data in a table format
    by using Python’s tabulate module.
    '''
    
   
    rows = [[s.country, s.code, s.product, s.cost, s.quantity] for s in shoe_list]
    
    return print(tabulate(rows, headers= headers,tablefmt= "grid"))
    


def order_shoe_list_by_q():
    n = len(shoe_list)-1
    for i in range(n):
        for j in range(n-i):
            if shoe_list[j].quantity > shoe_list[j+1].quantity:
                shoe_list[j],shoe_list[j+1]= shoe_list[j+1], shoe_list[j]
    return shoe_list
     

def re_stock():
    pass
    '''
    This function will find the shoe object with the lowest quantity,
    which is the shoes that need to be re-stocked. Ask the user if they
    want to add this quantity of shoes and then update it.
    This quantity should be updated on the file for this shoe.
    '''
    order_shoe_list_by_q()
    
    choice = input(f"{shoe_list[0].product} is low on stock there is {shoe_list[0].quantity} available do you want to restock? (Y/N)").lower()
    
    if choice == "y":
        restock = int(input("How many would you like to add? "))
        print(f"adding {restock} items to {shoe_list[0].product} " )
        shoe_list[0].quantity += restock
        print(f"There are now {shoe_list[0].quantity} of the {shoe_list[0].product}'s")
        with open(file_path,"w+") as file:
            file.write(f"Country,Code,Product,Cost,Quantity\n")
            for i in range(len(shoe_list)):
                file.write(str(shoe_list[i]).strip()+f"\n")
                
    else:
        return None
    
    
    
    
    
def search_shoe():
    pass
    '''
     This function will search for a shoe from the list
     using the shoe code and return this object so that it will be printed.
    '''
  
    target = input("Enter a shoe code to search for: ")
    
    for i in range(len(shoe_list)):
       if str(shoe_list[i].code).strip() == target.strip():
           row = [[shoe_list[i].country,shoe_list[i].code, shoe_list[i].product, shoe_list[i].cost, shoe_list[i].quantity]]
    print(tabulate(row, headers=headers, tablefmt="grid"))

  

    
    
    
    
    
def value_per_item():
    pass
    '''
    This function will calculate the total value for each item.
    Please keep the formula for value in mind: value = cost * quantity.
    Print this information on the console for all the shoes.
    '''
    rows = []
    for shoe in shoe_list:
        value = shoe.cost*shoe.quantity
        rows.append([
            shoe.code,
            shoe.product,
            shoe.cost,
            shoe.quantity,
            value
        ])
    print(tabulate(rows, headers=["Code", "Product", "Cost", "Qty", "Value"], tablefmt="grid"))
    
    
def highest_qty():
    pass
    '''
    Write code to determine the product with the highest quantity and
    print this shoe as being for sale.
    '''
    order_shoe_list_by_q()
    maxqty_shoe= shoe_list[-1]
    return print(f"{maxqty_shoe.product} is for sale")
#==========Main Menu=============
'''
Create a menu that executes each function above.
This menu should be inside the while loop. Be creative!
'''  
read_shoes_data()
while True:

    choice = input(f"--------------------\nMain Menu:\n--------------------\nPlease select if you would like to:\n1) View all shoes\n2) Restock shoes\n3) Search for a shoe\n4) Get the value of all stock\n5) Get the shoe that we have the most of\n6) capture_shoes\n7) Exit\n--------------------\n-->")
  
    if choice == "1":
        view_all()
    elif choice == "2":
        re_stock()
    elif choice == "3":
        search_shoe()
    elif choice == "4":
        value_per_item()
    elif choice == "5":
        highest_qty()
    elif choice == "6":
         capture_shoes()
    elif choice == "7":
            exit(0)
        
    else:
        print("not a valid option try again!")
