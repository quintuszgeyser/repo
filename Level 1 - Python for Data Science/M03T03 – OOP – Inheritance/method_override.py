#create adult class 
class adult():
    def __init__(self,name,  age,  hair_colour, eye_colour):
        self.name =name
        self.age = age
        self.hair_colour = hair_colour
        self.eye_colour =eye_colour
        
    def can_drive(self):
        print(f"Age is {self.age} so you can drive")

#Create child subclass
class child(adult):
    def can_drive(self):
        print(f"Age is {self.age} so you are not allowed to drive")



def get_user_inputs():
    
    fetures = ["name",  "age",  "hair_colour", "eye_colour"]
    user_features= []
    for feature in fetures:
            get_feature= input(f"Please provide your {feature}: ")
            user_features.append(get_feature)

    user_feat_dict = dict(zip(fetures,user_features))
    return user_feat_dict




def is_old_enough(user_feat_dict):
        if int(user_feat_dict["age"])<= 18:
         user = child(user_feat_dict["name"], user_feat_dict["age"], user_feat_dict["hair_colour"], user_feat_dict["eye_colour"])
         user.can_drive()
    #else  #create parent class
        else:
          user = adult(user_feat_dict["name"], user_feat_dict["age"], user_feat_dict["hair_colour"], user_feat_dict["eye_colour"])
          user.can_drive()  


#create main method
def main():
    #take user input that asks for   name,  age,  hair  colour,  and  eye  colour
 inputs = get_user_inputs()  
 is_old_enough(inputs)
 

main()
