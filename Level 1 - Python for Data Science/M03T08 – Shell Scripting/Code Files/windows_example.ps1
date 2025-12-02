
#create a menu and allow the user to make a choice
$menu = Read-Host  "Select an option below by entering a number:`n1 - list directories and file in the current directory`n2 - Create a new file in the current directory`n3 - Create a new folder in the current directory.`n"
while($menu -ne 4){
    if ( $menu -eq 1){
        #List all the directories
        ls
    }
    elseif ($menu -eq 2){
        #get the name of the file from the user and creating the file in the folder
        $file = Read-Host "Enter the name of the file that you want to create"

        #An if statement is create inside the body of the if statement (Nested-If statement)
        #Check if the file exist before creating it
        if(Test-Path -Path $file){
            Write-Output "The file named $file already exist"
        }
        else{
        #Create a new file
            New-Item  $file
            Write-Output "File with the name $file is created"
        }
    }
    elseif ($menu -eq 3){
        #get the name of the file from the user and creating the file in the folder
        $folder = Read-Host "Enter the name of the folder that you want to create"

        #An if statement is create inside the body of the if statement (Nested-If statement)
        #Check if the folder exist before creating it
        if(Test-Path -Path $folder){
            Write-Output "The folder named $folder already exist"
        }
        else{
            #create a new folder
            New-Item -Path $folder -ItemType Directory
            Write-Output "Folder with the name $folder is created"
        }
    }
    else{
        Write-Output "You have made an invalid choice."
    }

    $menu = Read-Host  "Select an option below by entering a number:`n1 - list directories and file in the current directory`n2 - Create a new file in the current directory`n3 - Create a new folder in the current directory.`n4 - Exit`n"
}
