# _recompile.py — 编译 .pyd
import subprocess, sys, os, shutil

PYTHON = r"C:\Users\26112\Desktop\SafeShrink\.venv313\Scripts\python.exe"
PYTHON_HOME = r"C:\Users\26112\AppData\Local\Programs\Python\Python313"
SRC = r"C:\Users\26112\Desktop\SafeShrink"
DIST = r"C:\Users\26112\Desktop\SafeShrink\dist\SafeShrink\_internal"

modules = ["slim_tab", "theme_manager"]

for mod in modules:
    src_file = os.path.join(SRC, f"{mod}.py")
    if not os.path.exists(src_file):
        print(f"[SKIP] {mod}.py not found")
        continue
    
    # Compile to C
    cmd_cy = [PYTHON, "-m", "cython", "--3str", src_file, "-o", os.path.join(SRC, f"{mod}.c")]
    print(f"[CYTHON] {mod}...")
    r = subprocess.run(cmd_cy, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  FAIL: {r.stderr[:200]}")
        continue
    
    # Compile C to .pyd
    c_file = os.path.join(SRC, f"{mod}.c")
    pyd_name = f"{mod}.cp313-win_amd64.pyd"
    pyd_out = os.path.join(SRC, pyd_name)
    lib_dir = os.path.join(PYTHON_HOME, "libs")
    inc_dir = os.path.join(PYTHON_HOME, "include")
    
    cmd_cl = [
        "cl", "/nologo", "/O2", "/W3", "/MD",
        f"/I{inc_dir}",
        c_file,
        f"/link", f"/LIBPATH:{lib_dir}",
        f"/OUT:{pyd_out}",
        "/DLL", "/EXPORT:PyInit_" + mod,
    ]
    print(f"[CL] {mod}...")
    r = subprocess.run(cmd_cl, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  FAIL: {r.stderr[:200]}")
        continue
    
    # Copy to dist
    dist_pyd = os.path.join(DIST, pyd_name)
    shutil.copy2(pyd_out, dist_pyd)
    sz = os.path.getsize(dist_pyd)
    print(f"  OK: {pyd_name} ({sz} bytes)")
    
    # Cleanup
    for ext in [".c", ".lib", ".exp"]:
        f = os.path.join(SRC, mod + ext)
        if os.path.exists(f): os.remove(f)

print("\nDone!")
