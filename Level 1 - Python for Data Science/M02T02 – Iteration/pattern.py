range = range(1,10) 

for i in range:
    
    if i <= len(range)/2:
     
        print('*'*i)
    elif i == len(range)-1:
        break

    else:
        
        print('*'*(len(range)-i))
        
    

