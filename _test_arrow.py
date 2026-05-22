import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication, QComboBox
from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QPixmap

app = QApplication([])

combo = QComboBox()
combo.addItems(['Option A', 'Option B'])
b64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAARElEQVR4nGNgoDVgBBFnr335T6wGJhBhrMUD1kgIGGvxMII1kAKYkHUTMp0BWQM+TcZI4uQ7CZct6HySbcAJSIkbvAAApG4KjDGFuusAAAAASUVORK5CYII='
css = f'''
QComboBox {{
    background-color: #2a2a2a;
    color: white;
    border: 1px solid #444;
    padding: 4px;
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
    background: #3a3a3a;
}}
QComboBox::down-arrow {{
    image: url({b64});
    width: 12px;
    height: 12px;
}}
'''
combo.setStyleSheet(css)
combo.resize(200, 40)
combo.show()
app.processEvents()

pix = combo.grab(QRect(0, 0, 200, 40))
pix.save(r'C:\Users\26112\Desktop\SafeShrink\_combo_arrow_test.png')
print('OK, saved')
