@echo off
pyinstaller --onefile --noconsole --icon=Icon_v5.ico --name ImageManager --distpath ./app/dist --workpath ./app/build manager.py
cls
echo by continuing you will delete the build folder
pause
rmdir app\build