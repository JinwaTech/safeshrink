# -*- coding: utf-8 -*-
"""结果对比对话框（文本 Token 对比 + 图片尺寸对比）"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


def _fmt_size(b):
    if b < 1024:
        return f"{b} B"
    if b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b / 1024 / 1024:.2f} MB"


class ResultCompareDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("处理结果")
        self.resize(400, 0)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.addStretch()

        self._info_label = QLabel()
        self._info_label.setWordWrap(True)
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._info_label)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    # ── 文本 / SSD 结果 ────────────────────────────────────────────
    def set_text_result(self, file_name, orig_size, new_size,
                        orig_len, new_len,
                        original_tokens=None, new_tokens=None):
        saved = orig_size - new_size
        saved_pct = saved / orig_size * 100 if orig_size else 0
        self._info_label.setText(
            f"<b>{file_name}</b><br><br>"
            f"原始大小：{_fmt_size(orig_size)}<br>"
            f"处理后大小：{_fmt_size(new_size)}<br>"
            f"节省：{_fmt_size(saved)} ({saved_pct:.1f}%)<br><br>"
            f"字符数：{orig_len:,} → {new_len:,}"
        )
        if original_tokens is not None and new_tokens is not None:
            tok_saved = original_tokens - new_tokens
            tok_pct = tok_saved / original_tokens * 100 if original_tokens else 0
            self._info_label.setText(
                self._info_label.text()
                + f"<br>Token：~{original_tokens:,} → ~{new_tokens:,}"
                f"（节省 {tok_saved:,} tokens, {tok_pct:.1f}%）"
            )

    # ── 图片结果 ───────────────────────────────────────────────────
    def set_image_result(self, file_name, orig_size, new_size,
                         orig_dimensions, new_dimensions):
        saved = orig_size - new_size
        saved_pct = saved / orig_size * 100 if orig_size else 0
        self._info_label.setText(
            f"<b>{file_name}</b><br><br>"
            f"原始尺寸：{orig_dimensions}<br>"
            f"压缩后尺寸：{new_dimensions}<br><br>"
            f"文件大小：{_fmt_size(orig_size)} → {_fmt_size(new_size)}<br>"
            f"节省：{saved_pct:.1f}%"
        )