import random
city_flight = input("Please enter the city you are flying to: ")
num_nights = int(input("Please enter the number of nights you will be staying in a hotel: "))
rental_days = int(input("Please enter number of days for which you will be hiring a car: "))


def hotel_cost(num_nights):
    hotel_cost= round(random.uniform(200,1000),2)*num_nights
    
    return hotel_cost
    
def plane_cost(city):
    if  city == "Paris":
         price=round(random.uniform(200,1000),2)
         
    elif city == "Johannesburg":
        price = round(random.uniform(1000,3000),2)
        
    else:
        price = 10000
    
    return price
    



def car_rental(rental_days):
    car_cost= round(random.uniform(200,1000),2)* rental_days
    
    return car_cost
     
def holiday_cost(city_flight,num_nights,rental_days):
    
    total_cost = round(hotel_cost(num_nights)+ plane_cost(city_flight)+ car_rental(rental_days),2)
    
    return "R" + str(total_cost)


hotel_total = hotel_cost(num_nights)
plane_total = plane_cost(city_flight)
car_total = car_rental(rental_days)
holiday_total = round(hotel_total + plane_total + car_total, 2)

# Display results neatly
print("\n------ HOLIDAY COST SUMMARY ------")
print(f"Destination: {city_flight}")
print(f"Hotel cost for {num_nights} nights: R{hotel_total:.2f}")
print(f"Flight cost to {city_flight}: R{plane_total:.2f}")
print(f"Car rental for {rental_days} days: R{car_total:.2f}")
print("----------------------------------")
print(f"Total holiday cost: R{holiday_total:.2f}")
print("----------------------------------")