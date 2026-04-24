"""
文件减肥标签页
功能：压缩/精简 文件内容（文本文件 + 图片文件）
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QSlider, QCheckBox,
    QFrame, QFileDialog, QMessageBox, QComboBox,
    QStackedWidget, QSpinBox, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path
import os


class SlimTab(QWidget):
    file_processed = Signal(str, str)  # 原路径, 处理后内容

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.original_content = None
        self.processed_content = None  # 处理后的内容（用于撤销）
        self.current_mode = 'text'  # 'text' 或 'image'
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        # 文件选择区域（固定顶部）
        file_section = self.create_file_section()
        layout.addWidget(file_section)

        # 可滚动内容区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(16)

        # 堆叠窗口：文本选项 vs 图片选项
        self.stacked_options = QStackedWidget()
        # 让内容自然高度，不限制最小高度

        # 文本文件选项
        self.text_options = self.create_text_options()
        self.stacked_options.addWidget(self.text_options)

        # 图片文件选项
        self.image_options = self.create_image_options()
        self.stacked_options.addWidget(self.image_options)

        scroll_layout.addWidget(self.stacked_options)

        # 内容编辑区域（仅文本模式）
        self.content_section = self.create_content_section()
        scroll_layout.addWidget(self.content_section, 1)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        # 操作按钮（固定底部）
        actions_section = self.create_actions_section()
        layout.addWidget(actions_section)

    def load_settings(self):
        """从 settings.json 加载设置到 UI 控件"""
        import json
        from pathlib import Path
        # 使用与 settings_tab.py 相同的路径逻辑
        base = Path(__file__).parent
        if not base.exists():
            base = Path(r'C:\Users\26112\Desktop\SafeShrink')
        settings_file = base / 'settings.json'
        if not settings_file.exists():
            return
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            # 压缩强度
            if hasattr(self, 'slider'):
                self.slider.setValue(int(settings.get('text_compression', 50)))
            # 图片质量
            if hasattr(self, 'img_quality_slider'):
                self.img_quality_slider.setValue(int(settings.get('image_quality', 60)))
        except Exception:
            pass

    def refresh_from_settings(self, settings):
        """从设置标签页同步参数"""
        if hasattr(self, 'slider'):
            self.slider.setValue(int(settings.get('text_compression', 50)))
        if hasattr(self, 'img_quality_slider'):
            self.img_quality_slider.setValue(int(settings.get('image_quality', 60)))
        if hasattr(self, 'chk_embed_images'):
            self.chk_embed_images.setChecked(bool(settings.get('embed_images', True)))

    def create_file_section(self):
        frame = QFrame()
        frame.setObjectName("card")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)

        self.file_label = QLabel("未选择文件")
        self.file_label.setObjectName("subtitle")

        btn_browse = QPushButton("选择文件...")
        btn_browse.clicked.connect(self.browse_file)

        # 文件类型指示器
        self.file_type_label = QLabel("")
        self.file_type_label.setStyleSheet("color: #7c3aed; font-size: 12px;")

        layout.addWidget(self.file_label)
        layout.addWidget(self.file_type_label)
        layout.addStretch()
        layout.addWidget(btn_browse)

        return frame

    def create_text_options(self):
        """文本文件压缩选项"""
        from PySide6.QtWidgets import QFormLayout

        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        title = QLabel("压缩选项")
        title.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(title)

        # 使用表单布局
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # 处理模式
        self.format_combo = QComboBox()
        self.format_combo.addItems(["标准压缩", "激进压缩", "保留结构", "转换为SSD"])
        self.format_combo.setToolTip("标准压缩：基础文本压缩\n深度清理：移除注释、空行等\n保留结构：只清理格式问题")
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        form.addRow("处理模式:", self.format_combo)

        # 压缩强度
        slider_widget = QWidget()
        slider_layout = QHBoxLayout(slider_widget)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.setMinimumWidth(150)
        self.slider_value = QLabel("50%")
        self.slider.setMinimumWidth(40)
        self.slider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.slider, 1)
        slider_layout.addWidget(self.slider_value)
        form.addRow("压缩强度:", slider_widget)

        layout.addLayout(form)

        # 压缩效果说明
        self.effect_label = QLabel("效果：基础清理 + 去除重复字符 + 移除多余空格")
        self.effect_label.setStyleSheet("color: #7c3aed; font-size: 12px;")
        layout.addWidget(self.effect_label)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("divider")
        layout.addWidget(separator)

        # 选项复选框（文本模式）
        self.chk_remove_comments = QCheckBox("移除注释")
        self.chk_remove_comments.setChecked(False)

        self.chk_remove_ai = QCheckBox("去除AI写作痕迹")
        self.chk_remove_ai.setChecked(False)

        self.chk_resize_image = QCheckBox("缩小图片尺寸")
        self.chk_resize_image.setChecked(False)
        self.chk_resize_image.setToolTip("当图片超过设定尺寸时自动缩小")

        self.chk_embed_images = QCheckBox("转换SSD时嵌入图片（Base64）")
        self.chk_embed_images.setChecked(True)
        self.chk_embed_images.setToolTip(
            "勾选：图片转为Base64内嵌，SSD为单文件但体积变大\n"
            "不勾选：只保留文字引用，文件更小（推荐）"
        )
        self.chk_embed_images.setVisible(False)  # SSD模式下才显示

        layout.addWidget(self.chk_remove_comments)
        layout.addWidget(self.chk_remove_ai)
        layout.addWidget(self.chk_resize_image)
        layout.addWidget(self.chk_embed_images)

        layout.addStretch()

        return frame
        """图片文件压缩选项"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("图片压缩选项")
        title.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(title)

        # 图片信息
        self.img_info_label = QLabel("尺寸: - | 大小: - | 格式: -")
        self.img_info_label.setStyleSheet("color: #8b92a5; font-size: 12px;")
        layout.addWidget(self.img_info_label)

        # 图片压缩强度
        quality_layout = QHBoxLayout()
        quality_label = QLabel("图片压缩强度:")
        self.img_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.img_quality_slider.setRange(10, 100)
        self.img_quality_slider.setValue(60)
        self.img_quality_value = QLabel("60%")
        self.img_quality_slider.valueChanged.connect(self.on_image_quality_changed)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.img_quality_slider)
        quality_layout.addWidget(self.img_quality_value)

        # 尺寸限制
        size_group = QGroupBox("尺寸限制（可选）")
        size_layout = QVBoxLayout(size_group)
        self.img_chk_resize = QCheckBox("启用尺寸限制")

        size_input_layout = QHBoxLayout()
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("最大宽度:"))
        self.img_spin_width = QSpinBox()
        self.img_spin_width.setRange(100, 10000)
        self.img_spin_width.setValue(1920)
        self.img_spin_width.setSuffix(" px")
        self.img_spin_width.setEnabled(False)

        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("最大高度:"))
        self.img_spin_height = QSpinBox()
        self.img_spin_height.setRange(100, 10000)
        self.img_spin_height.setValue(1080)
        self.img_spin_height.setSuffix(" px")
        self.img_spin_height.setEnabled(False)

        self.img_chk_resize.stateChanged.connect(
            lambda checked: (
                self.img_spin_width.setEnabled(checked),
                self.img_spin_height.setEnabled(checked)
            )
        )
        self.img_chk_aspect = QCheckBox("保持宽高比")
        self.img_chk_aspect.setChecked(True)

        size_input_layout.addLayout(width_layout)
        size_input_layout.addLayout(height_layout)
        size_layout.addWidget(self.img_chk_resize)
        size_layout.addLayout(size_input_layout)
        size_layout.addWidget(self.img_chk_aspect)

        layout.addLayout(quality_layout)
        layout.addWidget(size_group)

        return frame

    def create_image_options(self):
        """图片文件压缩选项"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("图片压缩选项")
        title.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(title)

        # 图片信息
        self.img_info_label = QLabel("尺寸: - | 大小: - | 格式: -")
        self.img_info_label.setStyleSheet("color: #8b92a5; font-size: 12px;")
        layout.addWidget(self.img_info_label)

        # 图片压缩强度
        quality_layout = QHBoxLayout()
        quality_label = QLabel("图片压缩强度:")
        self.img_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.img_quality_slider.setRange(10, 100)
        self.img_quality_slider.setValue(60)
        self.img_quality_value = QLabel("60%")
        self.img_quality_slider.valueChanged.connect(self.on_image_quality_changed)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.img_quality_slider)
        quality_layout.addWidget(self.img_quality_value)

        # 尺寸限制
        size_group = QGroupBox("尺寸限制（可选）")
        size_layout = QVBoxLayout(size_group)
        self.img_chk_resize = QCheckBox("启用尺寸限制")

        size_input_layout = QHBoxLayout()
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("最大宽度:"))
        self.img_spin_width = QSpinBox()
        self.img_spin_width.setRange(100, 10000)
        self.img_spin_width.setValue(1920)
        self.img_spin_width.setSuffix(" px")
        self.img_spin_width.setEnabled(False)

        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("最大高度:"))
        self.img_spin_height = QSpinBox()
        self.img_spin_height.setRange(100, 10000)
        self.img_spin_height.setValue(1080)
        self.img_spin_height.setSuffix(" px")
        self.img_spin_height.setEnabled(False)

        self.img_chk_resize.stateChanged.connect(
            lambda checked: (
                self.img_spin_width.setEnabled(checked),
                self.img_spin_height.setEnabled(checked)
            )
        )
        self.img_chk_aspect = QCheckBox("保持宽高比")
        self.img_chk_aspect.setChecked(True)

        size_input_layout.addLayout(width_layout)
        size_input_layout.addLayout(height_layout)
        size_layout.addWidget(self.img_chk_resize)
        size_layout.addLayout(size_input_layout)
        size_layout.addWidget(self.img_chk_aspect)

        layout.addLayout(quality_layout)
        layout.addWidget(size_group)

        return frame

    def create_content_section(self):
        """内容编辑区域"""
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)

        title = QLabel("文件内容")
        title.setStyleSheet("font-weight: 600; font-size: 14px;")

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("文件内容将在此处显示...")

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #8b92a5; font-size: 12px;")

        layout.addWidget(title)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.stats_label)

        return frame

    def create_actions_section(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_process = QPushButton("处理文件")
        self.btn_process.setEnabled(False)
        self.btn_process.clicked.connect(self.process_file)

        self.btn_undo = QPushButton("撤销")
        self.btn_undo.setObjectName("danger")
        self.btn_undo.setEnabled(False)
        self.btn_undo.clicked.connect(self.undo_process)

        self.btn_save = QPushButton("保存结果")
        self.btn_save.setObjectName("secondary")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_result)

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("color: #10b981; font-weight: 500;")

        layout.addWidget(self.result_label)
        layout.addStretch()
        layout.addWidget(self.btn_undo)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_process)

        return frame

    def set_file(self, file_path):
        """设置文件（供拖拽使用）"""
        self.current_file = file_path
        self.file_label.setText(Path(file_path).name)
        self.detect_file_type(file_path)
        self.btn_process.setEnabled(True)
        self.btn_undo.setEnabled(False)  # 重置撤销按钮
        self.processed_content = None  # 清除处理内容
        self.result_label.setText("")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "所有支持的文件 (*.txt *.md *.json *.csv *.xml *.html *.docx *.jpg *.jpeg *.png *.gif *.bmp *.webp);;文本文件 (*.txt *.md *.json *.csv *.xml *.html *.docx);;图片文件 (*.jpg *.jpeg *.png *.gif *.bmp *.webp);;所有文件 (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.file_label.setText(Path(file_path).name)
            self.detect_file_type(file_path)
            self.btn_process.setEnabled(True)
            self.result_label.setText("")

    def detect_file_type(self, path):
        """检测文件类型并切换对应界面"""
        ext = Path(path).suffix.lower()
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

        if ext in image_exts:
            self.current_mode = 'image'
            self.stacked_options.setCurrentWidget(self.image_options)
            self.content_section.setVisible(False)
            self.load_image_info(path)
            # 更新图片模式的预览效果
            quality = self.img_quality_slider.value()
            self.effect_label.setText(f"效果：图片质量 {quality}% {'+ 缩小尺寸' if self.img_chk_resize.isChecked() else ''}")
        else:
            self.current_mode = 'text'
            self.stacked_options.setCurrentWidget(self.text_options)
            self.content_section.setVisible(True)
            self.load_file_content(path)
            # 恢复文本模式的预览效果
            self.on_slider_changed(self.slider.value())

    def load_image_info(self, path):
        """加载图片信息"""
        try:
            from safe_shrink_gui import get_image_info_gui

            info = get_image_info_gui(path)
            if 'error' in info:
                self.img_info_label.setText(f"无法读取图片: {info['error']}")
                return

            self.original_info = info
            self.img_info_label.setText(
                f"尺寸: {info['dimensions']} | 大小: {info['size_str']} | 格式: {info['format']} ({info['mode']})"
            )

            # 设置默认值
            if info['width'] > 0 and info['height'] > 0:
                self.img_spin_width.setValue(min(info['width'], 1920))
                self.img_spin_height.setValue(min(info['height'], 1080))

        except Exception as e:
            self.img_info_label.setText(f"无法读取图片: {e}")

    def on_format_changed(self, index):
        """处理模式变化"""
        modes = ["标准压缩", "深度清理", "保留结构", "转换为SSD"]
        mode = modes[index] if index < len(modes) else "标准压缩"

        # 隐藏/显示压缩强度滑块（SSD转换不需要）
        if mode == "转换为SSD":
            self.slider.setEnabled(False)
            self.effect_label.setText("将文档转换为SSD格式，提升大模型可读性")
            self.chk_embed_images.setVisible(True)
        else:
            self.slider.setEnabled(True)
            self.on_slider_changed(self.slider.value())
            self.chk_embed_images.setVisible(False)

    def on_slider_changed(self, value):
        """滑块变化时更新显示"""
        self.slider_value.setText(f"{value}%")

        # 根据压缩强度显示效果说明
        if value <= 10:
            effect = "基础清理（连续空行、多余空格）"
        elif value <= 30:
            effect = "基础清理 + 去除重复字符"
        elif value <= 50:
            effect = "基础清理 + 去除重复字符 + 移除多余空格"
        elif value <= 70:
            effect = "基础清理 + 去除重复字符 + 移除多余空格 + 移除括号内容"
        else:
            effect = "激进压缩：基础清理 + 去除重复字符 + 移除多余空格 + 移除括号和方括号"

        self.effect_label.setText(effect)

    def on_image_quality_changed(self, value):
        """图片质量滑块变化时更新显示"""
        self.img_quality_value.setText(f"{value}%")
        if self.current_mode == 'image':
            resize_text = " + 缩小尺寸" if self.img_chk_resize.isChecked() else ""
            self.effect_label.setText(f"效果：图片质量 {value}%{resize_text}")

    def load_file_content(self, path):
        try:
            from safe_shrink import read_file
            content = read_file(path)
            self.original_content = content
            self.text_edit.setPlainText(content)
            self.stats_label.setText(f"原文: {len(content)} 字符")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取文件: {e}")

    def process_file(self):
        if not self.current_file:
            return

        if self.current_mode == 'image':
            self.compress_image()
        else:
            self.process_text_file()

    def process_text_file(self):
        """处理文本文件"""
        if not self.current_file:
            return

        from safe_shrink_gui import slim_content, clean_docx_deep, clean_txt_md, convert_format_to_ssd

        mode = self.format_combo.currentText()
        ext = Path(self.current_file).suffix.lower()

        # 处理 SSD 转换
        if mode == "转换为SSD":
            try:
                from safe_shrink import estimate_tokens
                result = convert_format_to_ssd(self.current_file, embed_images=self.chk_embed_images.isChecked())
                self.processed_content = result
                self.text_edit.setPlainText(result)
                self.btn_save.setEnabled(True)
                self.btn_undo.setEnabled(True)

                orig_len = len(self.original_content) if self.original_content else 0
                new_len = len(result)

                # Token 对比
                orig_tokens = estimate_tokens(self.original_content) if self.original_content else None
                new_tokens = estimate_tokens(result) if result else None
                token_info = ""
                if orig_tokens and new_tokens:
                    token_saved = orig_tokens['total'] - new_tokens['total']
                    token_info = f" | Token: ~{orig_tokens['total']:,} → ~{new_tokens['total']:,}"
                    if token_saved > 0:
                        token_info += f" (省 {token_saved:,})"

                # 暂存 token，供保存历史时使用
                self._orig_tokens = orig_tokens
                self._new_tokens = new_tokens

                self.stats_label.setText(f"原文: {orig_len} 字符 → SSD: {new_len} 字符{token_info}")
                self.result_label.setText(f"✅ 已转换为 SSD 格式")
                return
            except Exception as e:
                QMessageBox.critical(self, "错误", f"转换失败: {e}")
                return

        if mode == "深度清理" and ext == '.docx':
            # Word 深度清理
            output = str(Path(self.current_file).with_suffix('.cleaned.docx'))
            result = clean_docx_deep(self.current_file, output, {
                'remove_empty_paragraphs': True,
                'remove_bullet_runs': True,
                'remove_non_image_shapes': True
            })

            if result['success']:
                stats = result['stats']
                msg = f"深度清理完成:\n"
                msg += f"- 移除空段落: {stats['empty_paragraphs_removed']}\n"
                msg += f"- 移除bullet字符: {stats['bullet_runs_removed']}\n"
                msg += f"- 移除形状: {stats['shapes_removed']}\n"
                msg += f"已保存到: {output}"
                QMessageBox.information(self, "完成", msg)
                self.btn_save.setEnabled(False)
            else:
                QMessageBox.critical(self, "错误", f"处理失败: {result['error']}")
        else:
            # 标准文本压缩
            content = self.text_edit.toPlainText()
            ratio = self.slider.value() / 100.0

            options = {
                'remove_comments': self.chk_remove_comments.isChecked(),
                'remove_ai': self.chk_remove_ai.isChecked(),
            }

            # 对 TXT/MD 做额外清理（区分处理）
            if ext == '.md':
                content = clean_txt_md(content, options, is_markdown=True)
            elif ext == '.txt':
                content = clean_txt_md(content, options, is_markdown=False)

            try:
                result = slim_content(content, ratio, options)
                self.processed_content = result  # 保存处理后的内容用于撤销
                self.text_edit.setPlainText(result)
                self.btn_save.setEnabled(True)
                self.btn_undo.setEnabled(True)  # 启用撤销按钮

                orig_len = len(self.original_content) if self.original_content else 0
                new_len = len(result)
                compress_rate = round((1 - new_len/orig_len) * 100, 1) if orig_len else 0

                # Token 简要显示
                from safe_shrink import estimate_tokens as _est
                ot = _est(self.original_content) if self.original_content else None
                nt = _est(result) if result else None
                token_info = ""
                if ot and nt:
                    ts = ot['total'] - nt['total']
                    token_info = f" | Token: ~{ot['total']:,} → ~{nt['total']:,}"
                    if ts > 0:
                        token_info += f" (省 {ts:,})"

                self.stats_label.setText(f"原文: {orig_len} 字符 → 压缩后: {new_len} 字符 (减少 {compress_rate}%){token_info}")
                self.result_label.setText(f"✅ 压缩完成，减少 {compress_rate}%")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"处理失败: {e}")

    def compress_image(self):
        """压缩图片"""
        if not self.current_file:
            return

        try:
            from safe_shrink_gui import compress_image_gui

            quality = self.img_quality_slider.value()

            # 尺寸限制
            max_w = self.img_spin_width.value() if self.img_chk_resize.isChecked() else None
            max_h = self.img_spin_height.value() if self.img_chk_resize.isChecked() else None

            # 临时输出
            ext = os.path.splitext(self.current_file)[1].lower()
            temp_output = self.current_file + '.compressed' + ext

            result = compress_image_gui(
                self.current_file,
                temp_output,
                quality=quality,
                max_width=max_w,
                max_height=max_h
            )

            if result['success']:
                saved = result['saved_percent']
                self.result_label.setText(
                    f"✅ 压缩成功！体积减少 {saved}% ({result['original_dimensions']} → {result['new_dimensions']})"
                )
                self.btn_save.setEnabled(True)
                self.btn_undo.setEnabled(True)
                self.compressed_path = result['output_path']
                self.show_compare_dialog_image(result)
            elif result.get('no_change'):
                self.result_label.setText(f"⚠️ {result.get('error', '图片已是最优状态，无法进一步压缩')}")
            else:
                QMessageBox.critical(self, "错误", f"压缩失败: {result.get('error')}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"压缩失败: {e}")

    def save_result(self):
        if not self.current_file:
            return

        if self.current_mode == 'image':
            self.save_image()
        else:
            self.save_text()

    def save_text(self):
        """保存文本文件"""
        # 根据当前模式生成默认文件名
        mode = self.format_combo.currentText()
        if mode == "转换为SSD":
            default_name = str(Path(self.current_file).with_suffix('.md'))
            file_filter = "Markdown文件 (*.md);;所有文件 (*.*)"
        else:
            default_name = str(Path(self.current_file).with_suffix('.slim.txt'))
            file_filter = "文本文件 (*.txt);;所有文件 (*.*)"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存文件",
            default_name,
            file_filter
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.result_label.setText(f"✅ 已保存到: {file_path}")
                self.btn_save.setEnabled(False)

                # 记录到历史（文本模式含 token 信息）
                if hasattr(self, '_orig_tokens') or mode == "转换为SSD":
                    try:
                        main_window = self.window()
                        orig_sz = os.path.getsize(self.current_file) if self.current_file and os.path.exists(self.current_file) else 0
                        new_sz = os.path.getsize(file_path)
                        orig_tok = getattr(self, '_orig_tokens', None)
                        new_tok = getattr(self, '_new_tokens', None)
                        if hasattr(main_window, 'history_manager'):
                            main_window.history_manager.add_record(
                                file_name=Path(self.current_file).name if self.current_file else "未知",
                                file_path=self.current_file,
                                action='slim',
                                original_size=int(orig_sz),
                                new_size=int(new_sz),
                                output_path=file_path,
                                original_tokens=orig_tok,
                                new_tokens=new_tok,
                            )
                            if hasattr(main_window, 'tab_history'):
                                main_window.tab_history.load_history()
                    except Exception as e:
                        print(f"保存历史失败: {e}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def undo_process(self):
        """撤销处理，恢复原始内容"""
        if not self.current_file:
            return

        reply = QMessageBox.question(
            self, "确认撤销", "确定要撤销处理，恢复原始内容吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.current_mode == 'text' and self.original_content:
                # 恢复文本内容
                self.text_edit.setPlainText(self.original_content)
                self.processed_content = None
                self.btn_undo.setEnabled(False)
                self.btn_save.setEnabled(False)

                # 更新统计
                orig_len = len(self.original_content)
                self.stats_label.setText(f"原文: {orig_len} 字符 (已撤销)")
                self.result_label.setText("↩️ 已撤销，恢复原始内容")

            elif self.current_mode == 'image':
                # 图片撤销：删除临时压缩文件
                if hasattr(self, 'compressed_path') and os.path.exists(self.compressed_path):
                    try:
                        os.remove(self.compressed_path)
                        delattr(self, 'compressed_path')
                    except:
                        pass

                self.btn_undo.setEnabled(False)
                self.btn_save.setEnabled(False)
                self.result_label.setText("↩️ 已撤销")

    def save_image(self):
        """保存图片"""
        if not hasattr(self, 'compressed_path'):
            return

        ext = Path(self.current_file).suffix
        default_name = Path(self.current_file).stem + '_compressed' + ext

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存图片",
            str(Path(self.current_file).parent / default_name),
            f"图片文件 (*{ext});;所有文件 (*.*)"
        )

        if save_path:
            import shutil
            try:
                shutil.move(self.compressed_path, save_path)
                self.result_label.setText(f"✅ 已保存到: {save_path}")
                self.btn_save.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def show_compare_dialog_text(self, orig_len, new_len):
        """显示文本文件对比对话框（含 Token 估算）"""
        from result_compare_dialog import ResultCompareDialog
        from safe_shrink import estimate_tokens

        # 获取文件大小
        import os
        orig_size = os.path.getsize(self.current_file) if self.current_file else 0

        # Token 估算
        orig_tokens = estimate_tokens(self.original_content) if self.original_content else None
        new_tokens = estimate_tokens(self.processed_content) if self.processed_content else None

        dialog = ResultCompareDialog(self)
        dialog.set_text_result(
            Path(self.current_file).name if self.current_file else "未知",
            orig_size,
            orig_size * new_len / orig_len if orig_len > 0 else 0,
            orig_len,
            new_len,
            original_tokens=orig_tokens,
            new_tokens=new_tokens
        )
        dialog.exec()

        # 保存到历史
        self.save_to_history(orig_size, orig_size * new_len / orig_len if orig_len > 0 else 0)

    def show_compare_dialog_image(self, result):
        """显示图片对比对话框"""
        from result_compare_dialog import ResultCompareDialog

        dialog = ResultCompareDialog(self)
        dialog.set_image_result(
            Path(self.current_file).name if self.current_file else "未知",
            result['original_size'],
            result['new_size'],
            result['original_dimensions'],
            result['new_dimensions']
        )
        dialog.exec()

        # 保存到历史
        self.save_to_history(result['original_size'], result['new_size'])

    def save_to_history(self, original_size, new_size, original_tokens=None, new_tokens=None):
        """保存到历史记录"""
        try:
            # 通过父窗口获取历史管理器
            main_window = self.window()
            if hasattr(main_window, 'history_manager'):
                main_window.history_manager.add_record(
                    file_name=Path(self.current_file).name if self.current_file else "未知",
                    file_path=self.current_file,
                    action='slim',
                    original_size=int(original_size),
                    new_size=int(new_size),
                    output_path=getattr(self, 'compressed_path', None),
                    original_tokens=original_tokens,
                    new_tokens=new_tokens,
                )
                # 刷新历史标签页
                if hasattr(main_window, 'tab_history'):
                    main_window.tab_history.load_history()
        except Exception as e:
            print(f"保存历史失败: {e}")

    def cleanup(self):
        """清理临时资源"""
        pass
    
    def update_language(self, lang):
        """更新语言"""
        from translations import get_translation
        _ = lambda t: get_translation(t, lang)
        
        # 更新文件选择区域
        if hasattr(self, 'file_label'):
            if '未选择' in self.file_label.text():
                self.file_label.setText(_('未选择文件'))
        
        # 更新按钮
        if hasattr(self, 'btn_process'):
            self.btn_process.setText(_('处理文件'))
        if hasattr(self, 'btn_undo'):
            self.btn_undo.setText(_('撤销'))
        if hasattr(self, 'btn_save'):
            self.btn_save.setText(_('保存结果'))
        
        # 更新文本选项区域
        if hasattr(self, 'format_combo'):
            items = [_('标准压缩'), _('激进压缩'), _('保留结构'), _('转换为SSD')]
            self.format_combo.clear()
            self.format_combo.addItems(items)
        
        # 更新复选框
        if hasattr(self, 'chk_remove_comments'):
            self.chk_remove_comments.setText(_('移除注释'))
        if hasattr(self, 'chk_remove_ai'):
            self.chk_remove_ai.setText(_('去除AI写作痕迹'))
        if hasattr(self, 'chk_resize_image'):
            self.chk_resize_image.setText(_('缩小图片尺寸'))
        
        # 更新图片选项区域
        if hasattr(self, 'img_info_label'):
            self.img_info_label.setText(_('尺寸: - | 大小: - | 格式: -'))
        if hasattr(self, 'img_chk_resize'):
            self.img_chk_resize.setText(_('启用尺寸限制'))
        if hasattr(self, 'img_chk_aspect'):
            self.img_chk_aspect.setText(_('保持宽高比'))
