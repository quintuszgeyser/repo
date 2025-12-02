tri1 = float(input("Len of first side "))
tri2 = float(input("Len of second side "))
tri3 = float(input("Len of third side "))
arr= [tri1,tri2,tri3]

s= sum(arr)/2

area = (s*(s-tri1)*(s-tri2)*(s-tri3))**0.5

print(area)