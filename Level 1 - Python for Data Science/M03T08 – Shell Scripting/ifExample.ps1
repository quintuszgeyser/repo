
$path = "."


if (Test-Path -Path "$path\new_folder") {

    New-Item -Path $path -Name "if_folder" -ItemType Directory -Force


    Set-Location -Path "$path\if_folder"

   
    New-Item -Name "inside_if_folder.txt" -ItemType File -Force


    Set-Location -Path $path
}


if (Test-Path -Path "$path\if_folder") {
    New-Item -Path $path -Name "hyperionDev" -ItemType Directory -Force
}
else {
    New-Item -Path $path -Name "new-projects" -ItemType Directory -Force
}

Get-ChildItem -Path $path -Directory
