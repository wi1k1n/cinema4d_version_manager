set APP_NAME=C4DVersionManager

@REM Create build.txt during packaging phase
python.exe buildinfo.py %APP_NAME%

@REM pyinstaller.exe --name "C4DVersionManager" "..\..\source\__init__.py" :: use this one to create default PyInstaller config
pyinstaller.exe .\%APP_NAME%.spec