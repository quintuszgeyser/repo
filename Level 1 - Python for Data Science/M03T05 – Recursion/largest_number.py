
list = [1,3,33,5,333,122,3,4,5,4]

def maxx(lst):
    if len(lst) ==1:
        return lst[0]
    
    else:
        submax = maxx(lst[1:])
        return lst[0] if  lst[0] > submax else submax


print(maxx(list))
   