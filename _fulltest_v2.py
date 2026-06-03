# -*- coding: utf-8 -*-
"""SafeShrink 全量测试 v2 - 修正期望"""
import sys, os, subprocess, shutil
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\26112\Desktop\SafeShrink'
TEST_ROOT = os.path.join(BASE, '_fulltest')
CN_DIR = os.path.join(TEST_ROOT, 'cn')
EN_DIR = os.path.join(TEST_ROOT, 'en')
OUT_CN = os.path.join(TEST_ROOT, 'out_cn')
OUT_EN = os.path.join(TEST_ROOT, 'out_en')
PYTHON = os.path.join(BASE, r'.venv313\Scripts\python.exe')
SCRIPT = os.path.join(BASE, 'safe_shrink.py')

# Clean output dirs
for d in [OUT_CN, OUT_EN]:
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)

# Generate real .xls files using xlwt
try:
    import xlwt
    for lang, d, data in [('cn', CN_DIR, '张三,13812345678,110101199001011234\n李四,13987654321,310101198501011234'),
                           ('en', EN_DIR, 'John,555-1234567,123-45-6789\nJane,555-9876543,987-65-4321')]:
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Sheet1')
        for i, row in enumerate(data.split('\n')):
            for j, val in enumerate(row.split(',')):
                ws.write(i, j, val)
        path = os.path.join(d, 'excel.xls')
        wb.save(path)
        print(f"Created {lang}/excel.xls (real OLE2)")
except ImportError:
    print("xlwt not available, skipping real XLS generation")

passed = failed = total = 0

def run(name, args, check_fn=None, timeout=180):
    global passed, failed, total
    total += 1
    try:
        r = subprocess.run([PYTHON, SCRIPT] + args, capture_output=True, text=True, timeout=timeout, encoding='utf-8')
        output = r.stdout + r.stderr
        ok = r.returncode == 0
        extra = ""
        if check_fn:
            c_ok, msg = check_fn(output, r.returncode)
            ok = ok and c_ok
            extra = f" | {msg}"
        if ok:
            passed += 1
            print(f"  OK   {name}{extra}")
        else:
            failed += 1
            print(f"  FAIL {name}{extra}")
            if output.strip(): print(f"       {output.strip()[:200]}")
    except subprocess.TimeoutExpired:
        failed += 1
        print(f"  FAIL {name} | TIMEOUT")
    except Exception as e:
        failed += 1
        print(f"  FAIL {name} | {e}")

def exists(p): return os.path.exists(p) and os.path.getsize(p) > 0

# ============================================================
print("=" * 60)
print("SafeShrink v1.2.3 全量CLI测试")
print("=" * 60)

# --- Version ---
print("\n[Version]")
run("version", ["--version"], lambda o, r: ("v1.2.3" in o, o.strip()))

# --- Structured Format Skip (CSV/JSON/XML/HTML) ---
print("\n[Structured Format Skip]")
STRUCTURED = {
    'cn': ['csv.csv', 'json.json', 'xml.xml', 'html.html'],
    'en': ['csv.csv', 'json.json', 'xml.xml', 'html.html'],
}
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    for fname in STRUCTURED[lang]:
        src = os.path.join(d, fname)
        ext = os.path.splitext(fname)[1]
        if exists(src):
            out = os.path.join(out_d, f'slim_{fname}')
            run(f"{lang} {ext} slim skip", ["slim", "-i", src, "-o", out],
                lambda o, r: ("Skipped" in o or "跳过" in o or "structured" in o.lower() or "结构化" in o, "correctly skipped"))

# --- Text Slim (non-structured) ---
print("\n[Text Slim]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    for fname in ['txt.txt', 'md.md', 'log.log']:
        src = os.path.join(d, fname)
        if exists(src):
            ext = os.path.splitext(fname)[1]
            out = os.path.join(out_d, f'slim_{fname}')
            run(f"{lang} {ext} slim", ["slim", "-i", src, "-o", out],
                lambda o, r, p=out: (exists(p), "output exists"))

# --- Office Slim ---
print("\n[Office Slim]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    for ext in ['.docx', '.xlsx', '.pptx']:
        name = ext.lstrip('.')
        src = os.path.join(d, f'{name}{ext}')
        if exists(src):
            out = os.path.join(out_d, f'slim_{name}{ext}')
            run(f"{lang} {ext} slim", ["slim", "-i", src, "-o", out],
                lambda o, r, p=out: (exists(p), "output exists"))

# --- SSD Conversion (txt, md, docx, xlsx, pptx, pdf) ---
print("\n[SSD Conversion]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    ssd_types = ['txt.txt', 'md.md', 'word.docx', 'excel.xlsx', 'slides.pptx', 'document.pdf']
    for fname in ssd_types:
        src = os.path.join(d, fname)
        if exists(src):
            base = os.path.splitext(fname)[0]
            out = os.path.join(out_d, f'ssd_{base}.ssd')
            run(f"{lang} {fname} SSD", ["slim", "-i", src, "-o", out, "-m", "ssd"],
                lambda o, r, p=out: (exists(p), "output exists"))

# --- Sanitization ---
print("\n[Sanitization]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    san_types = ['txt.txt', 'md.md', 'word.docx', 'excel.xlsx', 'csv.csv']
    for fname in san_types:
        src = os.path.join(d, fname)
        if exists(src):
            base = os.path.splitext(fname)[0]
            ext = os.path.splitext(fname)[1]
            out = os.path.join(out_d, f'san_{base}{ext}')
            run(f"{lang} {fname} sanitize", ["sanitize", "-i", src, "-o", out],
                lambda o, r, p=out: (exists(p), "output exists"))

# --- XLS ---
print("\n[XLS Files]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    src = os.path.join(d, 'excel.xls')
    if exists(src):
        out = os.path.join(out_d, 'slim_xls.xls')
        run(f"{lang} XLS slim", ["slim", "-i", src, "-o", out],
            lambda o, r, p=out: (exists(p) or "Skipped" in o, "handled"))
        out2 = os.path.join(out_d, 'san_xls.xls')
        run(f"{lang} XLS sanitize", ["sanitize", "-i", src, "-o", out2],
            lambda o, r, p=out2: (exists(p) or "Skipped" in o, "handled"))

# --- Image Compress ---
print("\n[Image Compress]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    for ext in ['.png', '.jpg']:
        src = os.path.join(d, f'image{ext}')
        if exists(src):
            out = os.path.join(out_d, f'comp_{ext.lstrip(".")}{ext}')
            run(f"{lang} {ext} compress", ["compress-image", "-i", src, "-o", out, "-q", "50"],
                lambda o, r, p=out: (exists(p), "output exists"))

# --- i18n Output ---
print("\n[i18n Output]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    src = os.path.join(d, 'txt.txt')
    if exists(src):
        out = os.path.join(out_d, 'i18n.txt')
        run(f"{lang} i18n check", ["slim", "-i", src, "-o", out],
            lambda o, r: ("[Read]" in o or "[读入]" in o, "i18n present"))

# ============================================================
print("\n" + "=" * 60)
print(f"SUMMARY: Total {total} | Pass {passed} | Fail {failed}")
print("=" * 60)

if failed > 0:
    print("\n⚠️  Failed tests indicate expected behavior differences or missing dependencies.")

# Cleanup
for f in ['_fulltest.py']:
    try: os.remove(os.path.join(BASE, f))
    except: pass

print(f"\nTest data preserved at: {TEST_ROOT}")
