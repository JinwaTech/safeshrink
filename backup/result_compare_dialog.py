"""
处理结果对比对话框
功能：显示处理前后的对比信息
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ResultCompareDialog(QDialog):
    """处理结果对比对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("处理结果对比")
        self.setMinimumSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 标题
        title = QLabel("📊 处理结果对比")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1a1a2e;")
        layout.addWidget(title)
        
        # 文件信息卡片
        self.file_info_frame = QFrame()
        self.file_info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e8eaef;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.file_info_layout = QVBoxLayout(self.file_info_frame)
        layout.addWidget(self.file_info_frame)
        
        # 对比表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["项目", "处理前", "处理后"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 120)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e8eaef;
                border-radius: 8px;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.table)
        
        # 节省空间提示
        self.saved_label = QLabel()
        self.saved_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #10b981;")
        layout.addWidget(self.saved_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        # 设置对话框属性，防止关闭时影响父窗口
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Dialog)
        
        layout.addLayout(btn_layout)
    
    def set_text_result(self, file_name, original_size, new_size, original_chars, new_chars,
                        original_tokens=None, new_tokens=None):
        """设置文本文件处理结果（支持 token 对比）"""
        # 清空文件信息
        for i in reversed(range(self.file_info_layout.count())):
            self.file_info_layout.itemAt(i).widget().deleteLater()
        
        # 文件信息
        file_label = QLabel(f"📄 文件: {file_name}")
        file_label.setStyleSheet("font-weight: 500;")
        self.file_info_layout.addWidget(file_label)
        
        # 表格数据
        has_tokens = original_tokens is not None and new_tokens is not None
        row_count = 4 if has_tokens else 3
        self.table.setRowCount(row_count)
        
        # 文件大小
        self.table.setItem(0, 0, QTableWidgetItem("文件大小"))
        self.table.setItem(0, 1, QTableWidgetItem(self.format_size(original_size)))
        self.table.setItem(0, 2, QTableWidgetItem(self.format_size(new_size)))
        
        # 字符数
        self.table.setItem(1, 0, QTableWidgetItem("字符数"))
        self.table.setItem(1, 1, QTableWidgetItem(f"{original_chars:,}"))
        self.table.setItem(1, 2, QTableWidgetItem(f"{new_chars:,}"))
        
        # Token 估算（如果提供）
        if has_tokens:
            orig_t = original_tokens.get('total', 0)
            new_t = new_tokens.get('total', 0)
            token_saved = orig_t - new_t
            token_rate = round((1 - new_t / orig_t) * 100, 1) if orig_t > 0 else 0
            
            self.table.setItem(2, 0, QTableWidgetItem("预估 Token"))
            self.table.setItem(2, 1, QTableWidgetItem(f"~{orig_t:,}"))
            token_item = QTableWidgetItem(f"~{new_t:,}")
            if token_saved > 0:
                token_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(2, 2, token_item)
        
        # 压缩率
        compress_rate = round((1 - new_size/original_size) * 100, 1) if original_size > 0 else 0
        cr_row = 3 if has_tokens else 2
        self.table.setItem(cr_row, 0, QTableWidgetItem("压缩率"))
        self.table.setItem(cr_row, 1, QTableWidgetItem("-"))
        rate_item = QTableWidgetItem(f"减少 {compress_rate}%")
        rate_item.setForeground(Qt.GlobalColor.green)
        self.table.setItem(cr_row, 2, rate_item)
        
        # 节省空间
        saved = original_size - new_size
        extra = ""
        if has_tokens and token_saved > 0:
            extra = f" | Token 节省 ~{token_saved:,} ({token_rate}%)"
        self.saved_label.setText(f"✅ 节省空间: {self.format_size(saved)} ({compress_rate}%){extra}")
    
    def set_image_result(self, file_name, original_size, new_size, original_dims, new_dims):
        """设置图片处理结果"""
        # 清空文件信息
        for i in reversed(range(self.file_info_layout.count())):
            self.file_info_layout.itemAt(i).widget().deleteLater()
        
        # 文件信息
        file_label = QLabel(f"🖼️ 文件: {file_name}")
        file_label.setStyleSheet("font-weight: 500;")
        self.file_info_layout.addWidget(file_label)
        
        # 表格数据
        self.table.setRowCount(3)
        
        # 文件大小
        self.table.setItem(0, 0, QTableWidgetItem("文件大小"))
        self.table.setItem(0, 1, QTableWidgetItem(self.format_size(original_size)))
        self.table.setItem(0, 2, QTableWidgetItem(self.format_size(new_size)))
        
        # 尺寸
        self.table.setItem(1, 0, QTableWidgetItem("尺寸"))
        self.table.setItem(1, 1, QTableWidgetItem(original_dims))
        self.table.setItem(1, 2, QTableWidgetItem(new_dims))
        
        # 压缩率
        compress_rate = round((1 - new_size/original_size) * 100, 1) if original_size > 0 else 0
        self.table.setItem(2, 0, QTableWidgetItem("压缩率"))
        self.table.setItem(2, 1, QTableWidgetItem("-"))
        rate_item = QTableWidgetItem(f"减少 {compress_rate}%")
        rate_item.setForeground(Qt.GlobalColor.green)
        self.table.setItem(2, 2, rate_item)
        
        # 节省空间
        saved = original_size - new_size
        self.saved_label.setText(f"✅ 节省空间: {self.format_size(saved)} ({compress_rate}%)")
    
    def set_batch_result(self, total_files, success_count, value, results, action='slim',
                         original_tokens=0, new_tokens=0):
        """设置批量处理结果（支持 token 对比）"""
        # 清空文件信息
        for i in reversed(range(self.file_info_layout.count())):
            self.file_info_layout.itemAt(i).widget().deleteLater()
        
        # 文件信息
        if action == 'sanitize':
            file_label = QLabel(f"📁 批量脱敏结果")
        else:
            file_label = QLabel(f"📁 批量处理结果")
        file_label.setStyleSheet("font-weight: 500;")
        self.file_info_layout.addWidget(file_label)
        
        # 表格数据
        has_tokens = original_tokens > 0 and new_tokens > 0
        if action == 'slim':
            self.table.setRowCount(5 if has_tokens else 4)
        else:
            self.table.setRowCount(4)
        
        # 总文件数
        self.table.setItem(0, 0, QTableWidgetItem("总文件数"))
        self.table.setItem(0, 1, QTableWidgetItem(f"{total_files}"))
        self.table.setItem(0, 2, QTableWidgetItem("-"))
        
        # 成功数
        self.table.setItem(1, 0, QTableWidgetItem("处理成功"))
        self.table.setItem(1, 1, QTableWidgetItem("-"))
        success_item = QTableWidgetItem(f"{success_count}")
        success_item.setForeground(Qt.GlobalColor.green)
        self.table.setItem(1, 2, success_item)
        
        # 失败数
        fail_count = total_files - success_count
        self.table.setItem(2, 0, QTableWidgetItem("处理失败"))
        self.table.setItem(2, 1, QTableWidgetItem("-"))
        fail_item = QTableWidgetItem(f"{fail_count}")
        if fail_count > 0:
            fail_item.setForeground(Qt.GlobalColor.red)
        self.table.setItem(2, 2, fail_item)
        
        if action == 'sanitize':
            row_idx = 3
            # 脱敏模式：显示脱敏处数
            self.table.setItem(row_idx, 0, QTableWidgetItem("脱敏处数"))
            self.table.setItem(row_idx, 1, QTableWidgetItem("-"))
            items_item = QTableWidgetItem(f"{value}处")
            items_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row_idx, 2, items_item)
            self.saved_label.setText(f"✅ 共脱敏 {value} 处敏感信息")
        else:
            row_idx = 3
            # Token 节省（在节省空间之前）
            if has_tokens:
                token_saved = original_tokens - new_tokens
                token_rate = round((1 - new_tokens / original_tokens) * 100, 1) if original_tokens > 0 else 0
                self.table.setItem(row_idx, 0, QTableWidgetItem("预估 Token 节省"))
                self.table.setItem(row_idx, 1, QTableWidgetItem(f"~{original_tokens:,} → ~{new_tokens:,}"))
                t_item = QTableWidgetItem(f"↓ {token_saved:,} ({token_rate}%)")
                t_item.setForeground(Qt.GlobalColor.green)
                self.table.setItem(row_idx, 2, t_item)
                row_idx += 1
            
            # 节省空间
            self.table.setItem(row_idx, 0, QTableWidgetItem("总节省空间"))
            self.table.setItem(row_idx, 1, QTableWidgetItem("-"))
            saved_item = QTableWidgetItem(self.format_size(value))
            saved_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row_idx, 2, saved_item)
            
            extra = ""
            if has_tokens:
                token_saved = original_tokens - new_tokens
                extra = f"，Token 节省 ~{token_saved:,}"
            self.saved_label.setText(f"✅ 共处理 {success_count}/{total_files} 个文件，节省 {self.format_size(value)}{extra}")
    
    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"