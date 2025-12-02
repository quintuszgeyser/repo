list = [27, -3, 4, 5, 35, 2, 1, -40, 7, 18, 9, -1, 16, 100]


def search(list, target):
    for i in range(0, len(list)):
        if list[i] == target:
            return i
        
    return None
        
        
print(search(list,9)) #used sequential search because algorythm is simple and the list is small


def insersion_sort(mylist):
    n = len(mylist)
    for i in range(1,n):
      insert_index = i
      current_value = mylist.pop(i)
      for j in range(i-1, -1, -1):
        if mylist[j] > current_value:
          insert_index = j
      mylist.insert(insert_index, current_value)

    return mylist



def binary_search(list, target):
    low = 0 
    high = len(list)-1
    
    
    while low <= high:
        
        mid = (low+high)//2
        
        if list[mid]:
            return mid
        
        elif target < list[mid]:
            high = mid -1
            
        else:
            low = mid +1
            
    return None


sorted_list = insersion_sort(list)

print(binary_search(sorted_list, 9))