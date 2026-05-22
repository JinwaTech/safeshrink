import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QWindow
from PySide6.QtCore import QTimer
import sys

app = QApplication(sys.argv)

# Find the SafeShrink window
windows = QApplication.topLevelWindows()
print(f"Found {len(windows)} windows")
for w in windows:
    print(f"  Title: {w.title()}, Visible: {w.isVisible()}")

# Try to grab the first visible window
for w in windows:
    if w.isVisible() and 'SafeShrink' in w.title():
        pix = w.grab()
        pix.save(r'C:\Users\26112\Desktop\SafeShrink\_ss_before.png')
        print(f'Saved {pix.width()}x{pix.height()} screenshot')
        break
else:
    print('SafeShrink window not found')
