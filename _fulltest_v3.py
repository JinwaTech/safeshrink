# -*- coding: utf-8 -*-
"""SafeShrink 全量测试 v3 - 最终版"""
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

for d in [OUT_CN, OUT_EN]:
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)

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

print("=" * 60)
print("SafeShrink v1.2.3 全量CLI测试 v3")
print("=" * 60)

# --- Version ---
print("\n[1. Version]")
run("version", ["--version"], lambda o, r: ("v1.2.3" in o, o.strip()))

# --- Structured Format Skip ---
print("\n[2. Structured Format Skip]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    for ext in ['.csv', '.json', '.xml', '.html']:
        src = os.path.join(d, f'{ext.lstrip(".")}{ext}')
        if exists(src):
            out = os.path.join(out_d, f'skip_{ext.lstrip(".")}{ext}')
            run(f"{lang} {ext} skip", ["slim", "-i", src, "-o", out],
                lambda o, r: ("Skipped" in o or "跳过" in o or "structured" in o.lower() or "结构化" in o, "correctly skipped"))

# --- Text Slim ---
print("\n[3. Text Slim]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    # .txt and .md
    for fname in ['txt.txt', 'md.md']:
        src = os.path.join(d, fname)
        if exists(src):
            out = os.path.join(out_d, f'slim_{fname}')
            run(f"{lang} {fname} slim", ["slim", "-i", src, "-o", out],
                lambda o, r, p=out: (exists(p), "output exists"))
    # .log — output saved as .txt (format downgrade)
    src = os.path.join(d, 'log.log')
    if exists(src):
        out = os.path.join(out_d, 'slim_log.txt')
        run(f"{lang} .log slim", ["slim", "-i", src, "-o", out],
            lambda o, r, p=out: (exists(p) or ".txt" in o, "format downgrade to .txt"))

# --- Office Slim ---
print("\n[4. Office Slim]")
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

# --- SSD Conversion ---
print("\n[5. SSD Conversion]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    for fname in ['txt.txt', 'md.md', 'word.docx', 'excel.xlsx', 'slides.pptx']:
        src = os.path.join(d, fname)
        if exists(src):
            base = os.path.splitext(fname)[0]
            out = os.path.join(out_d, f'ssd_{base}.ssd')
            run(f"{lang} {fname} SSD", ["slim", "-i", src, "-o", out, "-m", "ssd"],
                lambda o, r, p=out: (exists(p), "output exists"))
    # PDF SSD
    src = os.path.join(d, 'document.pdf')
    if exists(src):
        out = os.path.join(out_en if lang == 'en' else OUT_CN, 'ssd_document.ssd')
        run(f"{lang} PDF SSD", ["slim", "-i", src, "-o", out, "-m", "ssd"],
            lambda o, r, p=out: (exists(p), "output exists"))

# --- Sanitization ---
print("\n[6. Sanitization]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    for fname in ['txt.txt', 'md.md', 'word.docx', 'excel.xlsx', 'csv.csv']:
        src = os.path.join(d, fname)
        if exists(src):
            base = os.path.splitext(fname)[0]
            ext = os.path.splitext(fname)[1]
            out = os.path.join(out_d, f'san_{base}{ext}')
            run(f"{lang} {fname} sanitize", ["sanitize", "-i", src, "-o", out],
                lambda o, r, p=out: (exists(p), "output exists"))

# --- Image Compress ---
print("\n[7. Image Compress]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    for ext in ['.png', '.jpg']:
        src = os.path.join(d, f'image{ext}')
        if exists(src):
            out = os.path.join(out_d, f'comp_{ext.lstrip(".")}{ext}')
            run(f"{lang} {ext} compress", ["compress-image", "-i", src, "-o", out, "-q", "50"],
                lambda o, r, p=out: (exists(p), "output exists"))

# --- XLS (real OLE2 if xlwt available) ---
print("\n[8. XLS Files]")
try:
    import xlwt
    for lang, d, out_d in [('cn', CN_DIR, OUT_CN), ('en', EN_DIR, OUT_EN)]:
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Sheet1')
        ws.write(0, 0, 'Name')
        ws.write(0, 1, 'Phone')
        ws.write(1, 0, 'Test')
        ws.write(1, 1, '13800138000')
        path = os.path.join(d, 'real.xls')
        wb.save(path)
        out = os.path.join(out_d, 'slim_real.xls')
        run(f"{lang} XLS slim", ["slim", "-i", path, "-o", out],
            lambda o, r, p=out: (exists(p), "output exists"))
        out2 = os.path.join(out_d, 'san_real.xls')
        run(f"{lang} XLS sanitize", ["sanitize", "-i", path, "-o", out2],
            lambda o, r, p=out2: (exists(p), "output exists"))
except ImportError:
    print("  SKIP: xlwt not installed (pip install xlwt)")

# --- i18n ---
print("\n[9. i18n Output]")
for lang in ['cn', 'en']:
    d = CN_DIR if lang == 'cn' else EN_DIR
    out_d = OUT_CN if lang == 'cn' else OUT_EN
    src = os.path.join(d, 'txt.txt')
    if exists(src):
        out = os.path.join(out_d, 'i18n.txt')
        run(f"{lang} i18n", ["slim", "-i", src, "-o", out],
            lambda o, r: ("[Read]" in o or "[读入]" in o, "i18n present"))

# ============================================================
print("\n" + "=" * 60)
print(f"SUMMARY: Total {total} | Pass {passed} | Fail {failed}")
print("=" * 60)

if failed > 0:
    print("\nFailed tests:")
    # re-run failed to show details
    pass

print(f"\nTest data at: {TEST_ROOT}")
