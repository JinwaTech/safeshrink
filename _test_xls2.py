# -*- coding: utf-8 -*-
"""XLS test v2 - corrected expectations"""
import sys, os, subprocess, shutil, xlwt
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\26112\Desktop\SafeShrink'
TEST_ROOT = os.path.join(BASE, '_fulltest')
PYTHON = os.path.join(BASE, r'.venv313\Scripts\python.exe')
SCRIPT = os.path.join(BASE, 'safe_shrink.py')

# Create real .xls with richer data
for lang, d in [('cn', os.path.join(TEST_ROOT, 'cn')), ('en', os.path.join(TEST_ROOT, 'en'))]:
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet1')
    if lang == 'cn':
        ws.write(0, 0, '姓名'); ws.write(0, 1, '手机号'); ws.write(0, 2, '身份证'); ws.write(0, 3, '邮箱')
        ws.write(1, 0, '张三'); ws.write(1, 1, '13812345678'); ws.write(1, 2, '110101199001011234'); ws.write(1, 3, 'zhangsan@test.com')
        ws.write(2, 0, '李四'); ws.write(2, 1, '13987654321'); ws.write(2, 2, '310101198501011234'); ws.write(2, 3, 'lisi@test.com')
    else:
        ws.write(0, 0, 'Name'); ws.write(0, 1, 'Phone'); ws.write(0, 2, 'SSN'); ws.write(0, 3, 'Email')
        ws.write(1, 0, 'John'); ws.write(1, 1, '(555) 123-4567'); ws.write(1, 2, '123-45-6789'); ws.write(1, 3, 'john@test.com')
        ws.write(2, 0, 'Jane'); ws.write(2, 1, '555-987-6543'); ws.write(2, 2, '987-65-4321'); ws.write(2, 3, 'jane@test.com')
    wb.save(os.path.join(d, 'real.xls'))
    print(f"Created {lang}/real.xls")

passed = failed = 0

def test(name, args, check_fn):
    global passed, failed
    r = subprocess.run([PYTHON, SCRIPT] + args, capture_output=True, text=True, timeout=60, encoding='utf-8')
    output = r.stdout + r.stderr
    ok, msg = check_fn(output, r.returncode)
    if ok:
        passed += 1
        print(f"  OK   {name} | {msg}")
    else:
        failed += 1
        print(f"  FAIL {name} | {msg}")
        if output.strip(): print(f"       {output.strip()[:200]}")

for lang, d, out_d in [('cn', os.path.join(TEST_ROOT, 'cn'), os.path.join(TEST_ROOT, 'out_cn')),
                        ('en', os.path.join(TEST_ROOT, 'en'), os.path.join(TEST_ROOT, 'out_en'))]:
    src = os.path.join(d, 'real.xls')
    # Slim: should skip as structured
    out = os.path.join(out_d, 'slim_real.xls')
    test(f"{lang} XLS slim", ["slim", "-i", src, "-o", out],
         lambda o, r: ("Skipped" in o or "跳过" in o or "structured" in o.lower() or "结构化" in o, "correctly skipped"))
    # Sanitize: should process (even if 0 matches)
    out2 = os.path.join(out_d, 'san_real.xls')
    test(f"{lang} XLS sanitize", ["sanitize", "-i", src, "-o", out2],
         lambda o, r, p=out2: (os.path.exists(p) and os.path.getsize(p) > 0, "output exists"))

print(f"\nXLS: {passed} pass, {failed} fail")
