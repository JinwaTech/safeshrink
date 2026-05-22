@echo off
.venv312\Scripts\python.exe -c "import PySide6, fitz; print('PySide6:', PySide6.__version__); print('PyMuPDF:', fitz.__version__)"
echo.
.venv312\Scripts\python.exe -c "import openpyxl, docx, pptx; print('All OK')"