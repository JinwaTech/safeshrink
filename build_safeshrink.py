# -*- coding: utf-8 -*-
"""
SafeShrink Build Tool v2
改进：
1. hiddenimports 自动发现（build 前扫描所有 .py 文件，追加新模块到 spec）
2. _DEBUG 切换有 try/finally 保护，中途失败也一定恢复
3. 构建检测逻辑强化（不过度依赖单一字符串）
4. 残留进程清理增加等待重试
"""
import ast, os, re, shutil, subprocess, sys, time

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(PROJECT_DIR, 'main_window_v2.spec')
DIST_SRC = os.path.join(PROJECT_DIR, 'dist', 'main_window_v2')  # PyInstaller 默认输出（onedir 模式）
DIST_NEW = os.path.join(PROJECT_DIR, 'dist', 'SafeShrink')       # 最终目标路径
EXE_PATH = os.path.join(DIST_NEW, 'SafeShrink.exe')

# 不需要扫描的目录/文件（不参与 hiddenimports 发现）
IGNORE_DIRS = {'build', 'dist', '__pycache__', '.git', '.venv', 'venv'}
IGNORE_FILES = {'build.py', '__init__.py'}

# 标准库模块（不加入 hiddenimports）
STDLIB_MODULES = {
    'sys', 'os', 'time', 'datetime', 'threading', 'queue', 'pathlib',
    'json', 're', 'math', 'copy', 'shutil', 'subprocess', 'typing',
    'traceback', 'tempfile', 'zipfile', 'io', 'collections', 'abc',
    'functools', 'itertools', 'hashlib', 'base64', 'uuid', 'locale',
    'importlib', 'pkgutil', 'inspect', 'gc', 'weakref', 'warnings',
    'enum', 'struct', 'ctypes', 'socket', 'ssl', 'html', 'urllib',
    'http', 'xml', 'csv', 'configparser', 'argparse', 'logging',
    'atexit', 'signal', 'mmap', 'code', 'dis', 'opcode', 'pickle',
    'gzip', 'bz2', 'lzma', 'tarfile', 'fileinput', 'random', 'statistics',
    'cmath', 'decimal', 'fractions', 'numbers', 'operator', 'platform',
    'errno', 'codecs', 'string', 'textwrap', 'unicodedata',
}


# ─────────────────────────────────────────────
# 1. hiddenimports 自动发现
# ─────────────────────────────────────────────
def _scan_imports(py_path):
    """扫描一个 .py 文件，返回其中出现的所有 import 名称集合。"""
    imports = set()
    try:
        with open(py_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return imports

    # 匹配: import xxx / import xxx as yyy / import xxx, zzz
    for m in re.finditer(r'^import\s+([\w_][\w_,\s]*?)(?:\s*#.*)?$', content, re.MULTILINE):
        for part in m.group(1).split(','):
            name = part.strip().split()[0]
            if name:
                imports.add(name)

    # 匹配: from xxx import yyy / from xxx import (yyy, zzz) / from xxx import *
    for m in re.finditer(r'^from\s+([\w_][\w_\.]*)', content, re.MULTILINE):
        imports.add(m.group(1).strip())

    return imports


def _is_local_module(name, project_dir):
    """判断 name 是否为项目本地的 .py 模块（而非第三方包）。"""
    top = name.split('.')[0]
    if not top or top.startswith('_'):
        return False
    py_file = os.path.join(project_dir, top + '.py')
    return os.path.isfile(py_file)


def auto_discover_hiddenimports(project_dir):
    """
    扫描 project_dir 下所有 .py 文件，提取本地模块 import，
    返回需要强制加入 hiddenimports 的模块名列表（去重+排序）。
    """
    discovered = set()
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for fname in files:
            if not fname.endswith('.py') or fname in IGNORE_FILES:
                continue
            py_path = os.path.join(root, fname)
            imports = _scan_imports(py_path)
            for imp in imports:
                if imp not in STDLIB_MODULES and _is_local_module(imp, project_dir):
                    discovered.add(imp)

    return sorted(discovered)


# ─────────────────────────────────────────────
# 2. spec 文件 hiddenimports 注入
# ─────────────────────────────────────────────
def _inject_hiddenimports(discovered):
    """
    将 discovered 中的新模块追加到 spec 文件的 hiddenimports 列表。
    只追加不重复的模块，原 spec 文件其他内容不变。
    返回 (new_modules, existing_modules)。
    """
    if not discovered:
        return [], set()

    try:
        with open(SPEC_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 找到 hiddenimports=[ 所在行
        hi_start = None
        hi_end = None
        indent = None
        for i, line in enumerate(lines):
            m = re.match(r'^(\s*)hiddenimports\s*=\s*\[', line)
            if m:
                hi_start = i
                indent = m.group(1)
                break

        if hi_start is None:
            print('  [WARN] hiddenimports= not found in spec, skip')
            return [], set()

        # 找到对应的 ] 结束行（同缩进），可能有尾随逗号或其他字符
        for i in range(hi_start + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped in (']', '],') and lines[i].startswith(indent):
                hi_end = i
                break

        if hi_end is None:
            print('  [WARN] closing ] not found for hiddenimports, skip')
            return [], set()

        # 提取现有模块名
        existing = set()
        for i in range(hi_start + 1, hi_end):
            m = re.match(r'^\s*[\'"]([\w_]+)[\'"],?\s*$', lines[i])
            if m:
                existing.add(m.group(1))

        # 计算新增（仅未在列表中的）
        new_entries = [mod for mod in discovered if mod not in existing]

        if not new_entries:
            print(f'  [OK] hiddenimports already complete ({len(existing)} modules)')
            return [], existing

        # 在 ] 前插入新条目
        for mod in new_entries:
            lines.insert(hi_end, f'{indent}    "{mod}",\n')
            hi_end += 1

        with open(SPEC_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f'  [OK] Added {len(new_entries)} modules: {new_entries}')
        return new_entries, existing

    except Exception as e:
        print(f'  [ERROR] Failed to inject hiddenimports: {e}')
        return [], set()


# ─────────────────────────────────────────────
# 3. 残留进程清理
# ─────────────────────────────────────────────
def kill_residual_processes():
    """强制终止残留的 SafeShrink 进程，增加等待重试"""
    print('[0/5] Killing residual SafeShrink processes...')
    for attempt in range(3):
        subprocess.run(
            ['taskkill', '/F', '/IM', 'SafeShrink.exe', '/T'],
            capture_output=True
        )
        if attempt < 2:
            time.sleep(1)

    # 确认是否清理干净
    result = subprocess.run(
        ['tasklist', '/FI', 'IMAGENAME eq SafeShrink.exe'],
        capture_output=True, text=True
    )
    if 'SafeShrink.exe' in result.stdout:
        print('  [WARN] SafeShrink.exe still in process list')
    else:
        print('  [OK] No residual processes')


# ─────────────────────────────────────────────
# 4. 清理（带强制重试）
# ─────────────────────────────────────────────
def clean():
    for d in ['build', 'dist']:
        p = os.path.join(PROJECT_DIR, d)
        if not os.path.exists(p):
            continue
        for attempt in range(3):
            try:
                shutil.rmtree(p)
                print(f'[OK] Cleaned {d}/')
                break
            except PermissionError:
                if attempt < 2:
                    print(f'  [RETRY] {d}/ locked, retrying...')
                    time.sleep(2)
                    subprocess.run(
                        ['taskkill', '/F', '/IM', 'SafeShrink.exe', '/T'],
                        capture_output=True
                    )
                else:
                    print(f'  [WARN] {d}/ still locked, PyInstaller will overwrite')


# ─────────────────────────────────────────────
# 5. 构建
# ─────────────────────────────────────────────
def build():
    print('[1/4] Building with spec...')

    # 通过环境变量控制 sanitize_tab.py 的 _DEBUG 状态（不改源码）
    env = os.environ.copy()
    env['SAFE_SHRINK_DEBUG'] = 'False'  # 打包时关闭调试

    result = subprocess.run(
        [sys.executable, '-X', 'utf8', '-m', 'PyInstaller',
         '--noconfirm', SPEC_FILE],
        cwd=PROJECT_DIR,
        capture_output=True, text=True,
        encoding='utf-8', errors='replace',
        env=env
    )
    output = result.stdout + result.stderr

    # 强化错误检测
    FAIL_KEYWORDS = [
        'SyntaxError', 'ImportError', 'ModuleNotFoundError',
        'IndentationError', 'TabError', 'cannot find license',
        'Traceback (most recent call last):',
    ]
    has_error = any(kw in output for kw in FAIL_KEYWORDS)
    exit_ok = result.returncode == 0
    success_marker = 'Build complete' in output

    if exit_ok and success_marker and not has_error:
        print('[OK] Build complete')
        return True

    # 失败诊断
    print(f'[ERROR] Build failed (exit {result.returncode})')
    lines = [l for l in output.split('\n')
             if l.strip() and not l.strip().startswith('!')]
    print('  --- last output lines ---')
    for line in lines[-15:]:
        print(f'  {line}')
    return False


def rename_dist():
    """处理 PyInstaller 输出目录：
    - 如果 PyInstaller 已输出到 dist\SafeShrink（COLLECT 模式），直接重命名 EXE
    - 如果输出到 dist\main_window_v2（默认 onedir），复制并重命名
    """
    print('[2/4] Renaming dist directory...')
    
    # 情况1：PyInstaller 已输出到 dist\SafeShrink（COLLECT 模式）
    if os.path.exists(DIST_NEW):
        src_exe = os.path.join(DIST_NEW, 'main_window_v2.exe')
        dst_exe = os.path.join(DIST_NEW, 'SafeShrink.exe')
        
        if os.path.exists(src_exe):
            try:
                os.rename(src_exe, dst_exe)
                print(f'  [OK] Renamed main_window_v2.exe -> SafeShrink.exe')
            except Exception as e:
                print(f'  [ERROR] Failed to rename EXE: {e}')
                return False
        elif os.path.exists(dst_exe):
            print(f'  [OK] EXE already named SafeShrink.exe')
        else:
            print(f'  [WARN] EXE not found in {DIST_NEW}')
        
        return True
    
    # 情况2：PyInstaller 输出到 dist\main_window_v2（默认 onedir）
    if not os.path.exists(DIST_SRC):
        print(f'  [ERROR] Neither {DIST_NEW} nor {DIST_SRC} found')
        return False
    
    # 清理目标目录（如果存在）
    if os.path.exists(DIST_NEW):
        try:
            shutil.rmtree(DIST_NEW)
            print(f'  [OK] Cleaned old {DIST_NEW}')
        except Exception as e:
            print(f'  [WARN] Failed to clean old directory: {e}')
    
    # 复制整个目录
    try:
        shutil.copytree(DIST_SRC, DIST_NEW)
        print(f'  [OK] Copied {DIST_SRC} -> {DIST_NEW}')
    except Exception as e:
        print(f'  [ERROR] Failed to copy directory: {e}')
        return False
    
    # 重命名 EXE
    src_exe = os.path.join(DIST_NEW, 'main_window_v2.exe')
    dst_exe = os.path.join(DIST_NEW, 'SafeShrink.exe')
    
    if os.path.exists(src_exe):
        try:
            os.rename(src_exe, dst_exe)
            print(f'  [OK] Renamed main_window_v2.exe -> SafeShrink.exe')
        except Exception as e:
            print(f'  [ERROR] Failed to rename EXE: {e}')
            return False
    else:
        print(f'  [WARN] main_window_v2.exe not found, may already be named correctly')
    
    return True


def verify():
    print('[3/4] Verifying EXE...')
    if os.path.exists(EXE_PATH):
        sz = os.path.getsize(EXE_PATH) / 1e6
        print(f'[OK] EXE: {sz:.2f} MB')
        print(f'[OK] Path: {EXE_PATH}')
        assets = os.path.join(DIST_NEW, '_internal', 'assets')
        if os.path.exists(assets):
            items = os.listdir(assets)
            print(f'[OK] Assets: {len(items)} files ({", ".join(items)})')
        return True
    else:
        print(f'[ERROR] EXE not found: {EXE_PATH}')
        return False


def sync_to_desktop():
    print('[4/4] Creating desktop shortcut...')
    desktop_dir = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    shortcut_path = os.path.join(desktop_dir, 'SafeShrink.lnk')
    try:
        # 删除旧的 .lnk 文件
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
        # 杀掉残留进程（防止文件被锁）
        for attempt in range(3):
            result = subprocess.run(
                ['taskkill', '/F', '/IM', 'SafeShrink.exe', '/T'],
                capture_output=True
            )
            if os.path.exists(shortcut_path):
                try:
                    os.remove(shortcut_path)
                    break
                except PermissionError:
                    time.sleep(1)
            else:
                break
        # 创建快捷方式（通过 PowerShell WshShell）
        ps_script = (
            f"$ws = New-Object -ComObject WScript.Shell; "
            f"$sc = $ws.CreateShortcut('{shortcut_path}'); "
            f"$sc.TargetPath = '{EXE_PATH}'; "
            f"$sc.WorkingDirectory = '{os.path.dirname(EXE_PATH)}'; "
            f"$sc.WindowStyle = 1; "
            f"$sc.IconLocation = '{EXE_PATH},0'; "
            f"$sc.Save()"
        )
        subprocess.run(['powershell', '-ExecutionPolicy', 'ByPass', '-Command', ps_script],
                      capture_output=True, check=True)
        print(f'[OK] Shortcut created: {shortcut_path}')
        return True
    except Exception as e:
        print(f'[ERROR] Shortcut failed: {e}')
        return False


# ─────────────────────────────────────────────
# 6. _DEBUG 切换（有 always-finally 保护）
# ─────────────────────────────────────────────
DEBUG_FILES = ['slim_tab.py', 'sanitize_tab.py']


def set_debug_env(value):
    """切换 _DEBUG 状态（谨慎替换，只改第一个匹配）"""
    for fname in DEBUG_FILES:
        fpath = os.path.join(PROJECT_DIR, fname)
        if not os.path.exists(fpath):
            continue
        try:
            content = open(fpath, 'r', encoding='utf-8').read()
        except Exception:
            continue
        # 已经有环境变量机制的，跳过
        if 'SAFE_SHRINK_DEBUG' in content or 'SAFE_SHRINK_DEBUG' in os.environ:
            print(f'  [SKIP] {fname}: uses SAFE_SHRINK_DEBUG env')
            continue
        # 检查当前状态
        replace_from = '_DEBUG = False' if value else '_DEBUG = True'
        replace_to = '_DEBUG = True' if value else '_DEBUG = False'
        if replace_from not in content:
            print(f'  [SKIP] {fname}: already _DEBUG = {value}')
        elif replace_to in content:
            # 两个都有（理论上不可能），只改第一个
            content = content.replace(replace_from, replace_to, 1)
            open(fpath, 'w', encoding='utf-8').write(content)
            print(f'  [OK] {fname}: _DEBUG -> {value}')
        else:
            open(fpath, 'w', encoding='utf-8').write(
                content.replace(replace_from, replace_to, 1))
            print(f'  [OK] {fname}: _DEBUG -> {value}')


# ─────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────
if __name__ == '__main__':
    os.chdir(PROJECT_DIR)
    print('=' * 50)
    print('  SafeShrink Build Tool v2')
    print('=' * 50)

    # Step 0: 自动发现 hiddenimports
    print('\n[0/5] Auto-discovering hiddenimports...')
    discovered = auto_discover_hiddenimports(PROJECT_DIR)
    print(f'  Found {len(discovered)} local modules: {", ".join(discovered)}')

    # Step 0b: 注入新模块到 spec 文件
    print()
    new_mods, _ = _inject_hiddenimports(discovered)

    # Step 1: 终止残留进程
    print()
    kill_residual_processes()

    # Step 2: 清理旧构建
    print()
    clean()

    # Step 3: 设置 release 模式 _DEBUG=False
    print()
    print('[2/5] Setting _DEBUG = False...')
    set_debug_env(False)

    # Step 4: 构建（try/finally 保证恢复 _DEBUG）
    ok = False
    try:
        print()
        ok = build()
    finally:
        print()
        print('[5/5] Restoring _DEBUG = True (always)...')
        set_debug_env(True)

    # Step 5: 重命名 dist 目录
    print()
    if ok:
        ok = rename_dist()
    
    # Step 6: 验证和同步
    print()
    if ok:
        ok = verify()
    if ok:
        sync_to_desktop()

    if not ok:
        print('\n[ERROR] Build failed.')
        sys.exit(1)

    print()
    print('[OK] Done!')
