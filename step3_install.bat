@echo off
cd /d C:\Users\26112\Desktop\SafeShrink
echo pip upgrade...
.venv312\Scripts\pip.exe install --upgrade pip
echo.
echo Installing PySide6 and pymupdf...
.venv312\Scripts\pip.exe install PySide6==6.11.0 pymupdf
echo.
echo Installing other deps...
.venv312\Scripts\pip.exe install openpyxl python-docx python-pptx pdfminer.six chardet pillow xlsxwriter markitdown pdfplumber pypdf
echo.
echo Verify...
.venv312\Scripts\python.exe -c "import PySide6, fitz; print(PySide6.__version__, fitz.__version__)"
.venv312\Scripts\python.exe -c "import openpyxl, docx, pptx; print(ok)"
echo DONE