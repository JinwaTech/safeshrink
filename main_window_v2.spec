# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# ─── 强制收集完整包树（处理 lazy import） ───────────────────────────────
_markitdown_datas, _markitdown_binaries, _markitdown_hidden = collect_all('markitdown')
_azure_datas, _azure_binaries, _azure_hidden = collect_all('azure')
_docx_datas, _docx_binaries, _docx_hidden = collect_all('docx')
_openpyxl_datas, _openpyxl_binaries, _openpyxl_hidden = collect_all('openpyxl')
_pptx_datas, _pptx_binaries, _pptx_hidden = collect_all('pptx')
_pdfplumber_datas, _pdfplumber_binaries, _pdfplumber_hidden = collect_all('pdfplumber')
_pillow_datas, _pillow_binaries, _pillow_hidden = collect_all('PIL')
_doc2docx_datas, _doc2docx_binaries, _doc2docx_hidden = collect_all('doc2docx')
_pypdf_datas, _pypdf_binaries, _pypdf_hidden = collect_all('pypdf')

# beautifulsoup4 数据文件（子模块太多，只收集 datas）
_bs4_datas = collect_data_files('beautifulsoup4')

a = Analysis(
    ['main_window_v2.py'],
    pathex=[],
    binaries=(
        _markitdown_binaries + _azure_binaries +
        _docx_binaries + _openpyxl_binaries +
        _pptx_binaries + _pdfplumber_binaries +
        _pillow_binaries + _doc2docx_binaries + _pypdf_binaries
    ),
    datas=(
        [('assets', 'assets')] +
        [('settings_tab.py', '.')] +
        [('slim_tab.py', '.')] +
        [('sanitize_tab.py', '.')] +
        [('batch_tab.py', '.')] +
        [('history_tab.py', '.')] +
        [('history_manager.py', '.')] +
        [('theme_manager.py', '.')] +
        [('batch_processor.py', '.')] +
        [('file_status.py', '.')] +
        [('safe_shrink.py', '.')] +
        [('safe_shrink_gui.py', '.')] +
        [('result_compare_dialog.py', '.')] +
        [('format_to_ssd.py', '.')] +
        _markitdown_datas + _azure_datas +
        _docx_datas + _openpyxl_datas +
        _pptx_datas + _pdfplumber_datas +
        _pillow_datas + _doc2docx_datas + _pypdf_datas + _bs4_datas
    ),
    hiddenimports=(
        _markitdown_hidden + _azure_hidden +
        _docx_hidden + _openpyxl_hidden +
        _pptx_hidden + _pdfplumber_hidden +
        _pillow_hidden + _doc2docx_hidden + _pypdf_hidden +
        [
            'slim_tab',
            'sanitize_tab',
            'batch_tab',
            'history_tab',
            'history_manager',
            'settings_tab',
            'theme_manager',
            'batch_processor',
            'file_status',
            'safe_shrink',
            'safe_shrink_gui',
            'result_compare_dialog',
            'format_to_ssd',
            # markupsafe / markdown / markdownify / jinja2（markitdown 依赖）
            'markupsafe',
            'markdown',
            'markdownify',
            'jinja2',
            # PySide6 核心
            'PySide6.QtCore',
            'PySide6.QtGui',
            'PySide6.QtWidgets',
            'PySide6.QtNetwork',
            'PySide6.QtPrintSupport',
            # tqdm（doc2docx 依赖）
            'tqdm',
            'tqdm.auto',
            # win32com（doc2docx 运行时依赖）
            'win32com',
            'win32com.client',
            'pywintypes',
            'win32api',
            'pythoncom',
            # charset_normalizer / certifi（azure 依赖）
            'charset_normalizer',
            # numpy（部分模块需要）
            'numpy',
            'numpy._core',
            'numpy.libs',
        ]
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # PyMuPDF（已替换为 pypdf）
        'fitz',
        'pymupdf',
        # 不需要的模块
        'speech_recognition',
        'pocketsphinx',
        'vosk',
        'pypdfium2',
        'pypdfium2_raw',
        'tkinter',
        '_tkinter',
        'tk',
        'tcl',
        '_tcl_data',
        '_tk_data',
        'tcl8',
        'tcl86t',
        'PyQt6.QtQml',
        'PyQt6.QtQuick',
        'PyQt6.QtQuickWidgets',
        'PyQt6.QtWebEngine',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
        'PyQt6.Qt3D',
        'PyQt6.QtBluetooth',
        'PyQt6.QtLocation',
        'PyQt6.QtNfc',
        'PyQt6.QtPositioning',
        'PyQt6.QtRemoteObjects',
        'PyQt6.QtSensors',
        'PyQt6.QtSerialPort',
        'PyQt6.QtSql',
        'PyQt6.QtTest',
        'PyQt6.QtXml',
        'scipy',
        'sympy',
        'IPython',
        'jupyter',
        'notebook',
        'audioop',
        'sounddevice',
        'soundfile',
        'wave',
        'requests_oauthlib',
        'oauthlib',
        'httpx',
        'httpcore',
        'h11',
        'anyio',
        'sniffio',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SafeShrink',
    icon='assets/icon06_light.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main_window_v2',
)
