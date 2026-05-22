# build_selective.py
# SafeShrink Nuitka 自动化编译脚本
# 功能：监控全量编译完成 -> 分析 .o 文件 -> 输出链接命令
# 用法：python build_selective.py

import os, sys, time, re
from pathlib import Path

PROJECT_DIR   = r"C:\Users\26112\Desktop\SafeShrink"
BUILD_OUT_DIR = os.path.join(PROJECT_DIR, "nuitka313_out")
BUILD_LOG     = os.path.join(PROJECT_DIR, "nuitka_full_log.txt")

SAFE_SHRINK_MODULES = {
    "safe_shrink", "safe_shrink_gui", "slim_tab", "batch_tab",
    "batch_processor", "history_tab", "history_manager", "settings_tab",
    "theme_manager", "translations", "file_status", "format_to_ssd",
    "sanitize_ssd", "ssd_embed_images", "_ooxml_to_ssd",
}

EXCLUDE_MODULES = {
    "numpy", "pandas", "openpyxl", "xlsxwriter", "PIL", "pillow",
    "cryptography", "onnxruntime", "pypdfium2_raw", "pypdf", "fitz",
    "chardet", "charset_normalizer", "pdfminer", "markitdown",
    "reportlab", "pdf2image", "qrcode", "pyzbar", "numba",
    "sklearn", "scipy", "matplotlib", "tkinter",
}


def monitor_compilation(timeout_minutes=180):
    print("[1/3] 监控全量编译进度...")
    dist_dir = os.path.join(BUILD_OUT_DIR, "main_window_v2.dist")
    build_dir = os.path.join(BUILD_OUT_DIR, "main_window_v2.build")
    exe_path = os.path.join(dist_dir, "SafeShrink.exe")
    start_time = time.time()
    last_build_size = 0
    stable_rounds = 0

    while True:
        elapsed = (time.time() - start_time) / 60
        if elapsed > timeout_minutes:
            print(f"[错误] 超时 ({timeout_minutes} 分钟)")
            return False

        if os.path.exists(exe_path):
            exe_size = os.path.getsize(exe_path) / 1024 / 1024
            print(f"[完成] SafeShrink.exe 已生成: {exe_size:.1f} MB")
            return True

        if os.path.exists(build_dir):
            build_size = sum(
                f.stat().st_size for f in Path(build_dir).rglob("*") if f.is_file()
            ) / 1024 / 1024
            if build_size == last_build_size:
                stable_rounds += 1
            else:
                stable_rounds = 0
                last_build_size = build_size
            if stable_rounds >= 5:
                print(f"[警告] build 连续稳定在 {build_size:.0f} MB")
        else:
            build_size = 0

        print(f"  {time.strftime('%H:%M:%S')}  build={build_size:.0f}MB  elapsed={elapsed:.1f}min")
        time.sleep(60)


def extract_link_command():
    print("[2/3] 从日志提取链接命令...")
    if not os.path.exists(BUILD_LOG):
        print("  [警告] 日志文件不存在")
        return None

    with open(BUILD_LOG, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # 找包含 link.exe 的行，然后收集后续行
    link_cmd_lines = []
    in_link_cmd = False
    for line in lines:
        line = line.strip()
        if "link.exe" in line.lower() or "link " in line.lower():
            in_link_cmd = True
        if in_link_cmd:
            link_cmd_lines.append(line)
            # 链接命令通常以 .dll 或 .exe 结尾出现空行/独立行
            if line.endswith('".dll"') or line.endswith('".exe"') or ".obj" in line:
                break
            if len(link_cmd_lines) > 80:
                break

    if link_cmd_lines:
        full_cmd = "\n".join(link_cmd_lines)
        cmd_path = os.path.join(BUILD_OUT_DIR, "link_command_safeshrink.txt")
        with open(cmd_path, "w", encoding="utf-8") as f:
            f.write("# SafeShrink 专用链接命令（提取自 nuitka_full_log.txt）\n")
            f.write("# 在 Visual Studio Developer Command Prompt 里运行:\n")
            f.write("#   cd " + BUILD_OUT_DIR + "\\main_window_v2.build\n")
            f.write("#   " + full_cmd + "\n")
        print(f"  链接命令已保存: {cmd_path}")
        print(f"  命令长度: {len(full_cmd)} 字符")
        return full_cmd

    print("  [警告] 无法从日志提取链接命令")
    return None


def analyze_o_files():
    print("[3/3] 分析 .o 文件...")
    build_dir = os.path.join(BUILD_OUT_DIR, "main_window_v2.build")
    safeshink_o = []
    thirdparty_o = []
    other_o = []

    for root, dirs, files in os.walk(build_dir):
        for f in files:
            if not f.endswith(".o"):
                continue
            full_path = os.path.join(root, f)
            name = f.replace("module.", "").replace(".o", "")
            if name == "MainProgram" or name.startswith("_local_"):
                other_o.append(full_path)
                continue
            top = name.split(".")[0]
            if top in SAFE_SHRINK_MODULES:
                safeshink_o.append(full_path)
            elif top in EXCLUDE_MODULES:
                thirdparty_o.append(full_path)
            else:
                other_o.append(full_path)

    ss_sz  = sum(os.path.getsize(p) for p in safeshrink_o)  / 1024/1024
    tp_sz  = sum(os.path.getsize(p) for p in thirdparty_o)  / 1024/1024
    ot_sz  = sum(os.path.getsize(p) for p in other_o)       / 1024/1024

    print(f"  SafeShrink  .o: {len(safeshrink_o):4d} 个  ({ss_sz:8.1f} MB)")
    print(f"  第三方包    .o: {len(thirdparty_o):4d} 个  ({tp_sz:8.1f} MB)")
    print(f"  Python/其他 .o: {len(other_o):4d} 个  ({ot_sz:8.1f} MB)")

    # 保存列表
    list_path = os.path.join(BUILD_OUT_DIR, "safeshink_o_files.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for p in sorted(safeshrink_o):
            f.write(p + "\n")
    print(f"  SafeShrink .o 列表: {list_path}")

    print("\n" + "=" * 60)
    print("结论")
    print("=" * 60)
    print(f"  SafeShrink 代码: {ss_sz:.1f} MB ({len(safeshrink_o)} 个 .o)")
    print(f"  第三方包:        {tp_sz:.1f} MB ({len(thirdparty_o)} 个 .o)")
    if ss_sz < tp_sz:
        print(f"  -> SafeShrink 占比小，提取后 EXE 体积可大幅减少")

    return safeshink_o, thirdparty_o, other_o


def main():
    print("=" * 60)
    print("SafeShrink Nuitka 编译监控脚本")
    print("=" * 60)

    ok = monitor_compilation(timeout_minutes=180)
    if not ok:
        print("[错误] 编译失败或超时")
        sys.exit(1)

    extract_link_command()
    analyze_o_files()

    print("\n" + "=" * 60)
    print("下一步（明天查看）")
    print("=" * 60)
    print("  1. link_command_safeshrink.txt  -> 链接命令")
    print("  2. safeshink_o_files.txt        -> SafeShrink .o 清单")
    print("  3. nuitka313_out/main_window_v2.dist/SafeShrink.exe  -> 已可用 EXE")

if __name__ == "__main__":
    main()
