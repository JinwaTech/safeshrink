@echo off
cd /d C:\Users\26112\Desktop\SafeShrink
if exist .venv312 rmdir /s /q .venv312
"C:\Users\26112\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv312
echo VENV_DONE