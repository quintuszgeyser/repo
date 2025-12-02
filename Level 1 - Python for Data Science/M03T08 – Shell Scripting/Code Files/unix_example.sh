#!/bin/bash

#create a menu and allow the user to make a choice
echo  -e "Select an option below by entering a number:\n1 - list directories and file in the current directory\n2 - Create a new file in the current directory\n3 - Create a new folder in the current directory.\n"
read menu

while [ $menu -ne 4 ] 
do    	
    if [ $menu -eq 1 ]; then
        #list the directories and files in the current directory
        ls
    elif [ $menu -eq 2 ]; then
        #get the name of the file from the user and create the file in the folder
        echo "Enter the name of the file that you want to create"
        read file
    
        #An if statement is created inside the body of the if statement (Nested-If statement)
        #Check if the file exist before creating it
        if [ -f $file ]; then
            echo "The file named $file already exist"
        else
        #Create a new file
          touch $file
          echo "File with the name $file is created"
        fi
    elif [ $menu -eq 3 ]; then
        #get the name of the file from the user and create the file in the folder
        echo "Enter the name of the folder that you want to create"
        read folder
    
        #An if statement is created inside the body of the if statement (Nested-If statement)
        #Check if the folder exists before creating it
        if [ -d $folder ]; then
            echo "The folder named $folder already exist"
        
        else
            #create a new folder
            mkdir $folder
            echo "Folder with the name $folder is created"
        fi
    else
        #if the user enters a number that is not 1,2 or 3
        echo "You have made an invalid choice."
    fi
    #create a menu and allow the user to make a choice
    echo  -e "Select an option below by entering a number:\n1 - list directories and file in the current directory\n2 - Create a new file in the current directory\n3 - Create a new folder in the current directory.\n4 - Exit\n"
    read menu
done