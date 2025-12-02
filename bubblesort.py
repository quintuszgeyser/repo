

def bubblesort(list):
    n = len(list)
    for i in range(0,n-1):
        for j in range(0,n-1-i):
            if list[j]> list[j+1]:
                list[j],list[j+1] =list[j+1],list[j]
    return list

i = [1,2,3,2,1,4,54345,2,1,3,5,6]

print(bubblesort(i))




