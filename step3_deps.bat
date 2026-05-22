@echo off
REM Step 3: 安装 SafeShrink 依赖到 .venv312
cd /d C:\Users\26112\Desktop\SafeShrink

echo [1/3] 升级 pip...
.venv312\Scripts\pip.exe install --upgrade pip --quiet
echo pip 升级完成

echo [2/3] 安装核心包 PySide6 pymupdf...
.venv312\Scripts\pip.exe install PySide6==6.11.0 pymupdf --quiet
echo 核心包安装完成

echo [3/3] 安装其他依赖...
.venv312\Scripts\pip.exe install openpyxl python-docx python-pptx pdfminer.six chardet pillow xlsxwriter markitdown pdfplumber pypdf --quiet
echo 其他依赖安装完成

echo.
echo [验证] 测试关键包...
.venv312\Scripts\python.exe -c "import PySide6, fitz; print('PySide6:', PySide6.__version__); print('PyMuPDF:', fitz.__version__)"
echo.
echo Step 3 完成