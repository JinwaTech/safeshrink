import sys
print('sys.path[0]:', sys.path[0])
print('cwd:', sys.path[0])

import os
print('\nChecking safe_shrink locations:')

# Check上级目录
parent = r'C:\Users\26112\Desktop\SafeShrink'
test_pkg = os.path.join(parent, 'test_pkg')
ss_parent = os.path.join(parent, 'safe_shrink')
ss_test_pkg = os.path.join(test_pkg, 'safe_shrink')

print(f'上级 safe_shrink/ exists: {os.path.isdir(ss_parent)}')
print(f'test_pkg safe_shrink/ exists: {os.path.isdir(ss_test_pkg)}')

# Test import from上级目录
print('\nFrom 上级目录 (cwd):')
sys.path.insert(0, parent)
try:
    from safe_shrink.slim_tab import SlimTab
    print('  OK: imported from', ss_parent)
except ImportError as e:
    print('  FAIL:', e)

# Test import from test_pkg
print('\nFrom test_pkg (cwd):')
sys.path.insert(0, test_pkg)
try:
    from safe_shrink.slim_tab import SlimTab
    print('  OK: imported from', ss_test_pkg)
except ImportError as e:
    print('  FAIL:', e)