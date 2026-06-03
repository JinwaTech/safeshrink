# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# ── 收集第三方包 ──
_markitdown_d, _markitdown_b, _markitdown_h = collect_all('markitdown')
_magika_d, _magika_b, _magika_h = collect_all('magika')
_fitz_d, _fitz_b, _fitz_h = collect_all('fitz')
_pdfplumber_d, _pdfplumber_b, _pdfplumber_h = collect_all('pdfplumber')
_openpyxl_d, _openpyxl_b, _openpyxl_h = collect_all('openpyxl')
_pypdf_d, _pypdf_b, _pypdf_h = collect_all('pypdf')
_reportlab_d, _reportlab_b, _reportlab_h = collect_all('reportlab')
_xlrd_d, _xlrd_b, _xlrd_h = collect_all('xlrd')
_docx_d, _docx_b, _docx_h = collect_all('docx')
_pptx_d, _pptx_b, _pptx_h = collect_all('pptx')

a = Analysis(
    ['main_window_v2.py'],
    pathex=[],
    binaries=[
        # ── 项目核心 .pyd（Cython 编译） ──
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
        ('struct_sanitizer.cp313-win_amd64.pyd', '.'),
        ('history_manager.cp313-win_amd64.pyd', '.'),
        ('history_tab.cp313-win_amd64.pyd', '.'),
        ('settings_tab.cp313-win_amd64.pyd', '.'),
        ('theme_manager.cp313-win_amd64.pyd', '.'),
# translations.py 纯 .py 运行，不编译为 .pyd
        ('result_compare_dialog.cp313-win_amd64.pyd', '.'),
        # ── 第三方包 binaries ──
        *_markitdown_b, *_magika_b, *_fitz_b, *_pdfplumber_b,
        *_openpyxl_b, *_pypdf_b, *_reportlab_b, *_xlrd_b,
        *_docx_b, *_pptx_b,
    ],
    datas=[
        ('assets/icon06_light.ico', 'assets'),
        ('assets/arrow_up.png', 'assets'),
        ('assets/arrow_down.png', 'assets'),
        ('assets/arrow_down2.png', 'assets'),
        ('assets/icon06_64x64_light.png', 'assets'),
        ('assets/icon14_64x64_dark.png', 'assets'),
        # ── 第三方包数据 ──
        *_markitdown_d, *_magika_d, *_fitz_d, *_pdfplumber_d,
        *_openpyxl_d, *_pypdf_d, *_reportlab_d, *_xlrd_d,
        *_docx_d, *_pptx_d,
    ],
    hiddenimports=[
        # ── 第三方包 hidden imports ──
        *_markitdown_h, *_magika_h, *_fitz_h, *_pdfplumber_h,
        *_openpyxl_h, *_pypdf_h, *_reportlab_h, *_xlrd_h,
        *_docx_h, *_pptx_h,
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'Cython',
        'setuptools',
        'pip',
        'wheel',
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
