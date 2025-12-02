

list = [1,3,4,5,3,12,3,4,5,4]
i = 4


def sum(list, i):
    number = list[i]
    if i  == 0:
      return number   

    else:
        return number + sum(list,i-1)
    
print(sum(list,i))