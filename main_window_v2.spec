# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# markitdown 依赖链: markitdown -> magika -> onnxruntime
# 用 collect_submodules 获取模块名(用于 hiddenimports)
# 用 collect_data_files(include_py_files=True) 获取 .py 文件(用于 datas)
_markitdown_mods = collect_submodules('markitdown')
_markitdown_datas = collect_data_files('markitdown', include_py_files=True)
_magika_mods = collect_submodules('magika')
_magika_datas = collect_data_files('magika', include_py_files=True)
_onnxruntime_mods = collect_submodules('onnxruntime')
_onnxruntime_datas = collect_data_files('onnxruntime', include_py_files=True)
_fitz_mods = collect_submodules('fitz')
# Office 文件处理依赖
_pptx_mods = collect_submodules('pptx')
_pptx_datas = collect_data_files('pptx', include_py_files=True)
_openpyxl_mods = collect_submodules('openpyxl')
_openpyxl_datas = collect_data_files('openpyxl', include_py_files=True)
_pypdf_mods = collect_submodules('pypdf')
_pypdf_datas = collect_data_files('pypdf', include_py_files=True)

a = Analysis(
    ['main_window_v2.py'],
    pathex=[],
    # name 保持默认，PyInstaller 使用脚本名 main_window_v2
    # Cython-compiled .pyd modules (replaces .py source files)
    binaries=[
        ('safe_shrink.cp313-win_amd64.pyd', '.'),
        ('safe_shrink_gui.cp313-win_amd64.pyd', '.'),
        ('batch_processor.cp313-win_amd64.pyd', '.'),
        ('batch_tab.cp313-win_amd64.pyd', '.'),
        ('format_to_ssd.cp313-win_amd64.pyd', '.'),
        ('sanitize_ssd.cp313-win_amd64.pyd', '.'),
        ('ssd_embed_images.cp313-win_amd64.pyd', '.'),
        ('file_status.cp313-win_amd64.pyd', '.'),
        ('slim_tab.cp313-win_amd64.pyd', '.'),
        ('sanitize_tab.cp313-win_amd64.pyd', '.'),
        ('_ooxml_to_ssd.cp313-win_amd64.pyd', '.'),
    ],
    datas=[
        ('assets/icon06_light.ico', 'assets'),
        ('assets/arrow_up.png', 'assets'),
        ('assets/arrow_down.png', 'assets'),
        ('assets/arrow_down2.png', 'assets'),
        ('assets/icon06_64x64_light.png', 'assets'),
        ('assets/icon14_64x64_dark.png', 'assets'),
        ('.venv313/Lib/site-packages/fitz', 'fitz'),
        ('.venv313/Lib/site-packages/onnxruntime/capi', 'onnxruntime/capi'),
        ('.venv313/Lib/site-packages/pptx', 'pptx'),
        ('.venv313/Lib/site-packages/openpyxl', 'openpyxl'),
        ('.venv313/Lib/site-packages/pypdf', 'pypdf'),
    ] + _markitdown_datas + _magika_datas + _onnxruntime_datas + _pptx_datas + _openpyxl_datas + _pypdf_datas,
    hiddenimports=[
        'safe_shrink',
        'safe_shrink_gui',
        'batch_processor',
        'format_to_ssd',
        'sanitize_ssd',
        'ssd_embed_images',
        'sanitize_tab',
        'batch_tab',
        'slim_tab',
        'history_tab',
        'settings_tab',
        'theme_manager',
        'history_manager',
        'file_status',
        'translations',
        'result_compare_dialog',
        'fitz',
        'fitz.table',
        'fitz.utils',
        'docx',
        'pypdf',
        'PIL',
        'markitdown',
        'mammoth',
        'cobble',
        'xlrd',
        'magika',
        'onnxruntime',
        'pptx',
        'pptx.dmlc',
        'pptx.oxml',
        'pptx.presentation',
        'pptx.slide',
        'pptx.shape',
        'pptx.text',
        'pptx.table',
        'pptx.chart',
        'pptx.media',
        'pptx.util',
        'openpyxl',
        'openpyxl.worksheet',
        'openpyxl.workbook',
        'openpyxl.cell',
        'openpyxl.styles',
        'openpyxl.utils',
        'openpyxl.xml',
    ] + _markitdown_mods + _magika_mods + _onnxruntime_mods + _fitz_mods + _pptx_mods + _openpyxl_mods + _pypdf_mods,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon06_light.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SafeShrink',
)
