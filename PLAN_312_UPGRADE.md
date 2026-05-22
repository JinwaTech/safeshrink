# SafeShrink → Python 3.12 Nuitka 升级方案

**目标**：在 Python 3.12 下完成 Nuitka 编译，生成可运行的 SafeShrink.exe

---

## 步骤总览

| 步骤 | 内容 | 预计时间 |
|------|------|----------|
| Step 1 | 安装 Python 3.12 | 2-5 分钟 |
| Step 2 | 创建 .venv312 虚拟环境 | 1 分钟 |
| Step 3 | 安装所有依赖包 | 5-15 分钟 |
| Step 4 | 运行 Nuitka 编译 | 40-60 分钟 |
| Step 5 | 测试 EXE | 1 分钟 |
| Step 6 | 压缩打包发布 | 5 分钟 |

---

## Step 1：安装 Python 3.12

```powershell
# 下载 Python 3.12.10（64-bit）
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe" -OutFile "$env:TEMP\python312_setup.exe"

# 安装（添加 PATH，不装 launcher，忽略已安装警告）
Start-Process -FilePath "$env:TEMP\python312_setup.exe" -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0" -Wait

# 验证
& "C:\Users\26112\AppData\Local\Programs\Python\Python312\python.exe" --version
```

**验证成功标志**：`Python 3.12.10` 输出

---

## Step 2：创建虚拟环境

```powershell
cd C:\Users\26112\Desktop\SafeShrink

# 删除旧的（如果有）
if (Test-Path .venv312) { Remove-Item -Recurse -Force .venv312 }

# 创建 3.12 venv
& "C:\Users\26112\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv312

# 激活并验证
& .\.venv312\Scripts\Activate.ps1
python --version   # 应该是 3.12.10
```

**验证成功标志**：`Python 3.12.10`

---

## Step 3：安装依赖包

```powershell
# 激活 venv
Set-Location C:\Users\26112\Desktop\SafeShrink
& .\.venv312\Scripts\Activate.ps1

# 升级 pip
python -m pip install --upgrade pip

# 安装核心依赖（先装这些，验证兼容性）
pip install PySide6==6.11.0
pip install pymupdf

# 验证关键包
python -c "import PySide6; import fitz; print('PySide6:', PySide6.__version__); print('PyMuPDF:', fitz.__version__)"
```

**验证成功标志**：两个版本号都能打印出来，不报错

> ⚠️ 如果 PySide6 安装后 QApplication 报错，先跳过，继续装其他包，最后统一处理

---

## Step 4：安装其他 SafeShrink 依赖

```powershell
# 继续在 .venv312 中
pip install openpyxl python-docx python-pptx pdfminer.six chardet pillow
pip install xlsxwriter markitdown pdfplumber pypdf

# 验证
python -c "import openpyxl, docx, pptx; print('All OK')"
```

**验证成功标志**：`All OK`

---

## Step 5：运行 Nuitka 编译

```powershell
Set-Location C:\Users\26112\Desktop\SafeShrink
& .\.venv312\Scripts\Activate.ps1

# 编译命令（和 3.13 一样的参数，但没有 --include-package=io 了）
cmd /c "C:\Users\26112\AppData\Local\Programs\Python\Python312\python.exe -m nuitka --standalone --follow-imports --plugin-enable=pyside6 --windows-icon-from-ico=C:\Users\26112\Desktop\SafeShrink\assets\icon06_light.ico --windows-console-mode=disable --output-filename=SafeShrink.exe --output-dir=nuitka312_out --assume-yes-for-downloads main_window_v2.py 2>&1"
```

**验证成功标志**：`Nuitka: Successfully created '...\SafeShrink.exe'`

---

## Step 6：测试 EXE

```powershell
$exe = "C:\Users\26112\Desktop\SafeShrink\nuitka312_out\main_window_v2.dist\SafeShrink.exe"
$proc = Start-Process $exe -PassThru -WorkingDirectory (Split-Path $exe)
Start-Sleep 5
if ($proc.HasExited) {
    Write-Host "[失败] ExitCode: $($proc.ExitCode)"
} else {
    Write-Host "[成功] EXE 运行正常"
    Stop-Process $proc -Force
}
```

**验证成功标志**：`[成功] EXE 运行正常`

---

## 断点续做指南

如果在某步中断，恢复方式：

| 中断点 | 恢复命令 |
|--------|----------|
| Step 1 中断 | 重新运行 Step 1 安装命令 |
| Step 2 中断 | 运行 `if (Test-Path .venv312) {Remove-Item -Recurse .venv312}` 然后重做 Step 2 |
| Step 3 中断 | 直接继续运行 Step 3（pip 有断点续传） |
| Step 4 中断 | 检查 `nuitka312_out` 是否已有 build 目录，有则继续，无需重头 |

---

## 预期产出

- EXE 路径：`nuitka312_out\main_window_v2.dist\SafeShrink.exe`
- EXE 大小：约 120-150 MB
- 是否带图标：是（icon06_light.ico）
- 是否能运行：预期是
