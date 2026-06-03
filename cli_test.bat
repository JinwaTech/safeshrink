@echo off
chcp 65001 >nul
python -c "
import subprocess, os
os.chdir(r'C:\Users\26112\Desktop\SafeShrink')
r1 = subprocess.run([r'dist\SafeShrink\SafeShrink.exe', '--version'], capture_output=True, encoding='utf-8', errors='replace')
r2 = subprocess.run([r'dist\SafeShrink\SafeShrink.exe', '--check'], capture_output=True, encoding='utf-8', errors='replace')
print('=== SafeShrink CLI Test ===')
print()
print('--- --version ---')
print(r1.stdout.strip() if r1.stdout else '(no output)')
print(f'exit code: {r1.returncode}')
print()
print('--- --check ---')
out = r2.stdout.strip() if r2.stdout else '(no output)'
out = out.replace(chr(65533), '?')
print(out)
print(f'exit code: {r2.returncode}')
print()
input('Press Enter to continue...')
"
pause
