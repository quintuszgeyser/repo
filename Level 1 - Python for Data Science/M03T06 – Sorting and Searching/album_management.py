class Album:
    def __init__(self,album_name,number_of_songs,album_artist):
        self.album_name =album_name
        self.number_of_songs =number_of_songs
        self.album_artist =album_artist
        
        
        
        
    def __str__(self):  
        return f"{self.album_name},{self.album_artist},{self.number_of_songs}"
    

        
def order(list,order_by):
    n = len(list)
 

    for  i in range(n-1):
        for j in range(n-1 -i):
            if getattr(list[j],order_by) > getattr(list[j+1],order_by):
                list[j],list[j+1] =  list[j+1],list[j]
    return  list   
     
def search(lst, search_on, item):
    n = len(lst)
    front = 0
    back = n // 2
    while front < n // 2 or back < n:
        if front < n // 2 and getattr(lst[front], search_on) == item:
            return front
        if back < n and getattr(lst[back], search_on) == item:
            return back
        front += 1
        back += 1
    return -1


      
 
 
        
        
albumns1 = [Album("Headers",8,"Johan"),Album("Banges",2,"Pierre"),Album("James",7,"BJ"),Album("hearme",6,"Suzan"),Album("loer",5,"Liefer")]

sorted_albums = order(albumns1,"number_of_songs")
    
sorted_albums[0],sorted_albums[1] = sorted_albums[1],sorted_albums[0]
print(f"\nSorted by number of songs")    
for album in sorted_albums:
    print(album)
    
    
albumns2 = albumns1
albumns2.append( Album("Dark Side of the Moon", "Pink Floyd", 9)) 
albumns2.append(Album("Oops!... I Did It Again", "Britney Spears", 16))   
    
    
albumns2 = sorted(albumns2,key= lambda album: album.album_name.lower())

print(f"\nSorted by number of Album name")   
for album in albumns2:
    print(album)
    
    
print(f"\nIndex of item")    
    
print(search(albumns2, "album_name", "Dark Side of the Moon"))
