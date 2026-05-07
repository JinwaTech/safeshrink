"""测试 setPlainText 参数问题"""
import sys
from PySide6.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout

app = QApplication(sys.argv)

widget = QWidget()
layout = QVBoxLayout()
text_edit = QTextEdit()
layout.addWidget(text_edit)
widget.setLayout(layout)

# 测试 1: 正常调用
text_edit.setPlainText("测试文本")
print("测试 1 通过: setPlainText(str)")

# 测试 2: 传入 tuple
try:
    text_edit.setPlainText(("文本", 5))
    print("测试 2 通过: setPlainText(tuple)")
except TypeError as e:
    print(f"测试 2 失败: {e}")

# 测试 3: 解包 tuple
try:
    result = ("文本", 5)
    text_edit.setPlainText(*result)
    print("测试 3 通过: setPlainText(*tuple)")
except TypeError as e:
    print(f"测试 3 失败: {e}")

widget.show()
print("所有测试完成")
