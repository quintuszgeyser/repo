# PLEASE ENSURE YOU OPEN THIS FILE IN VS CODE otherwise you may not be able to read/edit it.

# *** NOTE ON COMMENTS ***
# This is a comment in Python.
# Comments can be placed anywhere in Python code and the computer ignores them -- they are intended to be read by humans.
# Any line with a # in front of it is a comment.
# Please read all the comments in this example file and all others.

clean_car_red = True
clean_car_blue = True
clean_car_green = True
num_of_car = 0
busy = False

print("Welcome to the car wash")

red_check = input(
    "Is the Red car Dirty? (Yes or No)"
)  # Note input is case sensitive here
if red_check == "Yes":
    clean_car_red = False

blue_check = input(
    "Is the Blue car Dirty? (Yes or No)"
)  # Note input is case sensitive here
if blue_check == "Yes":
    clean_car_blue = False

green_check = input(
    "Is the Green car Dirty? (Yes or No)"
)  # Note input is case sensitive here
if green_check == "Yes":
    clean_car_green = False

if clean_car_red == False:
    print("Red car really needs a cleaning")
    num_of_car += 1

if clean_car_blue == False:
    print("Blue car really needs a cleaning")
    num_of_car += 1

if clean_car_green == False:
    print("Green car really needs a cleaning")
    num_of_car += 1
    print(num_of_car)

if num_of_car == 3:
    busy = True

if busy == True:
    print("The car wash was was packed today")
