menu = ["Hamburger","Coffee","Toothpicks","Purity"]
prices = [45,28,2,12]
stock = [100,20,45,31]


stock =dict(zip(menu,stock))
price = dict( zip(menu,prices))

total_value = 0

for item in menu:
    total_value += stock[item]*price[item]
    

print(total_value)
