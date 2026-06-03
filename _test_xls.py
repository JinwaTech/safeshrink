# -*- coding: utf-8 -*-
"""XLS test with real OLE2 files"""
import sys, os, subprocess, shutil, xlwt
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\26112\Desktop\SafeShrink'
TEST_ROOT = os.path.join(BASE, '_fulltest')
PYTHON = os.path.join(BASE, r'.venv313\Scripts\python.exe')
SCRIPT = os.path.join(BASE, 'safe_shrink.py')

for lang, d in [('cn', os.path.join(TEST_ROOT, 'cn')), ('en', os.path.join(TEST_ROOT, 'en'))]:
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet1')
    if lang == 'cn':
        ws.write(0, 0, '姓名'); ws.write(0, 1, '手机号'); ws.write(0, 2, '身份证')
        ws.write(1, 0, '张三'); ws.write(1, 1, '13812345678'); ws.write(1, 2, '110101199001011234')
    else:
        ws.write(0, 0, 'Name'); ws.write(0, 1, 'Phone'); ws.write(0, 2, 'SSN')
        ws.write(1, 0, 'John'); ws.write(1, 1, '(555) 123-4567'); ws.write(1, 2, '123-45-6789')
    wb.save(os.path.join(d, 'real.xls'))
    print(f"Created {lang}/real.xls")

for lang, d, out_d in [('cn', os.path.join(TEST_ROOT, 'cn'), os.path.join(TEST_ROOT, 'out_cn')),
                        ('en', os.path.join(TEST_ROOT, 'en'), os.path.join(TEST_ROOT, 'out_en'))]:
    src = os.path.join(d, 'real.xls')
    for action, ext in [('slim', '.xls'), ('sanitize', '.xls')]:
        out = os.path.join(out_d, f'{action}_real{ext}')
        r = subprocess.run([PYTHON, SCRIPT, action, '-i', src, '-o', out],
                          capture_output=True, text=True, timeout=60, encoding='utf-8')
        ok = os.path.exists(out) and os.path.getsize(out) > 0
        status = "OK" if ok else "FAIL"
        print(f"  {status} {lang} XLS {action} (rc={r.returncode})")
        if not ok:
            combined = r.stdout + r.stderr
            if combined.strip():
                print(f"       {combined.strip()[:200]}")
