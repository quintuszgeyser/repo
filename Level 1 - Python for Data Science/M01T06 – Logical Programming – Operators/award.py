swimming_time = int(input("Swimming time: "))
cycling_time = int(input("cycling time: "))
running_time = int(input("running time: "))


total_time = swimming_time + cycling_time + running_time


print(f"Total time taken for the triathlon:" + str(total_time) + "minutes")


if total_time >= 111:
    print("No award") 

elif total_time >105:
     print("Provincial scroll")

elif total_time >100:
 print("Provincial half colours")
elif total_time >0:
 print("Provincial colours")
else:
 print("No award")

