
$path = "."


New-Item -Path "$path\Folder1" -ItemType Directory -Force
New-Item -Path "$path\Folder2" -ItemType Directory -Force
New-Item -Path "$path\Folder3" -ItemType Directory -Force


Set-Location -Path "$path\Folder1"


New-Item -Path "ChildFolder1" -ItemType Directory -Force
New-Item -Path "ChildFolder2" -ItemType Directory -Force
New-Item -Path "ChildFolder3" -ItemType Directory -Force


Set-Location -Path $path


Remove-Item -Path "$path\Folder2" -Recurse -Force
Remove-Item -Path "$path\Folder3" -Recurse -Force


Get-ChildItem -Path $path -Directory
