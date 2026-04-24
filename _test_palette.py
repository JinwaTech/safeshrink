"""测试 Qt QToolButton 颜色：setPalette vs setStyleSheet 优先级"""
import sys
from PySide6.QtWidgets import QApplication, QWidget, QToolButton, QVBoxLayout
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

app = QApplication(sys.argv)

# 父容器设 stylesheet（模拟日历导航栏的全局样式）
parent = QWidget()
parent.setStyleSheet('QWidget QToolButton { color: #333333; background: #f0f0f0; }')

# 子按钮 1：用 stylesheet 覆盖（模拟方案 A/B）
btn1 = QToolButton()
btn1.setText('Button via setStyleSheet')
btn1.setStyleSheet('QToolButton { color: #00ff00; background: transparent; }')

# 子按钮 2：用 QPalette 覆盖
btn2 = QToolButton()
btn2.setText('Button via setPalette')
palette = btn2.palette()
palette.setColor(QPalette.ColorRole.WindowText, QColor('#00ff00'))
btn2.setPalette(palette)

# 子按钮 3：用 setStyleSheet + 外部样式（看优先级）
btn3 = QToolButton()
btn3.setText('Button via setStyleSheet last')
# 先设父样式，再设自身样式
btn3.setStyleSheet('QToolButton { color: #00ff00; background: transparent; border: none; }')

layout = QVBoxLayout()
for btn in [btn1, btn2, btn3]:
    layout.addWidget(btn)
parent.setLayout(layout)
parent.show()

sys.exit(app.exec())