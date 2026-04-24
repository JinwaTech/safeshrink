"""
批量处理标签页
功能：批量压缩/脱敏整个文件夹
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QCheckBox, QFrame,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QRadioButton, QComboBox, QScrollArea, QSlider,
    QGridLayout, QSpinBox, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path


class BatchWorker(QThread):
    """后台处理线程（多线程并发）"""
    progress = pyqtSignal(int, int)       # 已完成数, 总数
    current_file = pyqtSignal(str)        # 当前正在处理的文件名
    file_done = pyqtSignal(str, bool, str, int)  # 文件名, 成功, 消息, 节省字节数
    finished = pyqtSignal()

    def __init__(self, folder, action, options):
        super().__init__()
        self.folder = folder
        self.action = action  # 'slim' or 'sanitize'
        self.options = options
        self._is_running = True
        self.total_saved = 0  # 累计节省空间
        self.total_orig_tokens = 0  # 处理前 token 总计
        self.total_new_tokens = 0   # 处理后 token 总计
        self._lock = __import__('threading').Lock()
        self._done_count = 0
        self._processed_records = []  # 处理记录（用于写入标记文件）

    def _process_one(self, file_path):
        """在子线程中处理单个文件，返回 (文件名, 成功, 消息, 节省字节数)"""
        from safe_shrink_gui import process_file_gui, clean_docx_deep
        import shutil
        from pathlib import Path

        folder = Path(self.folder)

        try:
            rel_path = file_path.relative_to(folder)

            if self.options.get('output_path'):
                output_base = Path(self.options['output_path'])
            elif self.options.get('backup', True):
                output_base = folder / 'output'
            else:
                output_base = folder

            output_path = output_base / rel_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            orig_size = file_path.stat().st_size
            ext = file_path.suffix.lower()
            is_supported = (
                ext in ('.txt', '.md', '.json', '.csv', '.xml', '.html',
                        '.docx', '.xlsx', '.xls', '.pptx', '.pdf',
                        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
            )

            if not is_supported:
                # 不可处理，直接复制
                shutil.copy2(file_path, output_path)
                with self._lock:
                    self._processed_records.append({
                        'original': file_path.name,
                        'output': file_path.name,
                        'type': 'copy',
                        'status': 'success'
                    })
                return (file_path.name, True, "复制", 0)

            saved_bytes = 0

            # Office 文档脱敏：保持格式原地处理（不含 PDF，PDF 走 batch_processor）
            if ext in ('.docx', '.xlsx', '.xls', '.pptx', '.ppt') and self.action == 'sanitize':
                types = self.options.get('sanitize_items', None)
                custom = self.options.get('custom_words', [])
                mode = self.options.get('mask_mode', 'mask')
                try:
                    from sanitize_tab import SanitizeTab
                    sanitizer = SanitizeTab.__new__(SanitizeTab)  # 无 __init__ 的 dummy 实例
                    # 输出路径加 _脱敏 后缀（保持格式）
                    out_file = output_path.with_stem(output_path.stem + '_脱敏')
                    if ext == '.docx':
                        from docx import Document
                        doc = Document(str(file_path))
                        sanitizer._sanitize_native_docx(doc, types, custom, mode)
                        doc.save(str(out_file))
                    elif ext in ('.xlsx', '.xls'):
                        from openpyxl import load_workbook
                        wb = load_workbook(str(file_path))
                        sanitizer._sanitize_native_xlsx(wb, types, custom, mode)
                        wb.save(str(out_file))
                    elif ext == '.pptx':
                        from pptx import Presentation
                        prs = Presentation(str(file_path))
                        sanitizer._sanitize_native_pptx(prs, types, custom, mode)
                        prs.save(str(out_file))
                    new_size = out_file.stat().st_size
                    saved_bytes = orig_size - new_size
                    with self._lock:
                        self._processed_records.append({
                            'original': file_path.name,
                            'output': out_file.name,
                            'type': self.action,
                            'status': 'success'
                        })
                    return (file_path.name, True, "完成", saved_bytes)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    shutil.copy2(file_path, output_path)
                    with self._lock:
                        self._processed_records.append({
                            'original': file_path.name,
                            'output': file_path.name,
                            'type': 'copy',
                            'status': 'success'
                        })
                    return (file_path.name, True, "复制", 0)

            elif ext == '.docx' and self.options.get('deep_clean', False):
                result = clean_docx_deep(str(file_path), str(output_path))
                if result['success']:
                    new_size = output_path.stat().st_size
                    saved_bytes = orig_size - new_size
                    with self._lock:
                        self._processed_records.append({
                            'original': file_path.name,
                            'output': file_path.name,
                            'type': 'slim',
                            'status': 'success'
                        })
                    return (file_path.name, True, "完成", saved_bytes)
                else:
                    shutil.copy2(file_path, output_path)
                    with self._lock:
                        self._processed_records.append({
                            'original': file_path.name,
                            'output': file_path.name,
                            'type': 'copy',
                            'status': 'success'
                        })
                    return (file_path.name, True, "复制", 0)

            elif ext == '.pdf':
                # 检查是否需要 SSD 转换
                if self.action == 'slim' and self.options.get('convert_to_ssd', False):
                    try:
                        from format_to_ssd import convert_to_ssd_v2, is_ssd_convertible
                        print(f"[DEBUG batch_tab] PDF SSD 转换已启用")
                        if is_ssd_convertible(str(file_path)):
                            ssd_content = convert_to_ssd_v2(str(file_path), optimize=True)
                            out_file = output_path.with_stem(output_path.stem + '_SSD').with_suffix('.md')
                            with open(str(out_file), 'w', encoding='utf-8') as f:
                                f.write(ssd_content)
                            new_size = out_file.stat().st_size
                            saved_bytes = orig_size - new_size
                            with self._lock:
                                self._processed_records.append({
                                    'original': file_path.name,
                                    'output': out_file.name,
                                    'type': 'ssd',
                                    'status': 'success'
                                })
                            return (file_path.name, True, "SSD", saved_bytes)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        print(f"[DEBUG batch_tab] PDF SSD 转换失败: {e}")

                # 脱敏或普通压缩
                opts = dict(self.options)
                opts['output_path'] = str(output_path)
                result = process_file_gui(str(file_path), self.action, opts)
                if result.get('success'):
                    # 写入结果内容
                    if result.get('content') and not result.get('direct_write'):
                        # PDF 脱敏后无法保持原格式，改为 .txt
                        out_file = output_path.with_stem(output_path.stem + '_脱敏').with_suffix('.txt')
                        with open(str(out_file), 'w', encoding='utf-8') as f:
                            f.write(result['content'])
                        new_size = out_file.stat().st_size
                    else:
                        new_size = output_path.stat().st_size
                    saved_bytes = orig_size - new_size
                    with self._lock:
                        self._processed_records.append({
                            'original': file_path.name,
                            'output': out_file.name if result.get('content') else file_path.name,
                            'type': self.action,
                            'status': 'success'
                        })
                    return (file_path.name, True, "完成", saved_bytes)
                else:
                    shutil.copy2(file_path, output_path)
                    with self._lock:
                        self._processed_records.append({
                            'original': file_path.name,
                            'output': file_path.name,
                            'type': 'copy',
                            'status': 'success'
                        })
                    return (file_path.name, True, "复制", 0)

            elif ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'):
                if self.action == 'slim':
                    from safe_shrink_gui import compress_image_gui
                    quality = self.options.get('image_quality', 60)
                    result = compress_image_gui(str(file_path), str(output_path), quality=quality)
                    if result['success']:
                        saved_bytes = result.get('size_reduced', 0)
                        saved = result.get('saved_percent', 0)
                        if saved > 0:
                            with self._lock:
                                self._processed_records.append({
                                    'original': file_path.name,
                                    'output': file_path.name,
                                    'type': 'slim',
                                    'status': 'success'
                                })
                            return (file_path.name, True, f"压缩 {saved}%", saved_bytes)
                        else:
                            shutil.copy2(file_path, output_path)
                            with self._lock:
                                self._processed_records.append({
                                    'original': file_path.name,
                                    'output': file_path.name,
                                    'type': 'copy',
                                    'status': 'success'
                                })
                            return (file_path.name, True, "复制", 0)
                    else:
                        shutil.copy2(file_path, output_path)
                        with self._lock:
                            self._processed_records.append({
                                'original': file_path.name,
                                'output': file_path.name,
                                'type': 'copy',
                                'status': 'success'
                            })
                        return (file_path.name, True, "复制", 0)
                else:
                    # 脱敏模式下图片直接复制
                    shutil.copy2(file_path, output_path)
                    with self._lock:
                        self._processed_records.append({
                            'original': file_path.name,
                            'output': file_path.name,
                            'type': 'copy',
                            'status': 'success'
                        })
                    return (file_path.name, True, "复制", 0)

            else:
                # 使用 batch_processor 来处理，支持 SSD 转换
                from batch_processor import process_file
                file_info = {
                    'path': str(file_path),
                    'name': file_path.name,
                    'ext': ext,
                    'relative_path': str(rel_path),
                    'size': orig_size
                }
                result = process_file(file_info, self.action, self.options, str(output_base))

                if result['status'] == 'success':
                    new_size = result['output_size']
                    saved_bytes = orig_size - new_size
                    with self._lock:
                        self._processed_records.append({
                            'original': file_path.name,
                            'output': result.get('output_name', ''),
                            'type': result.get('type', self.action),
                            'status': 'success',
                            'items_found': result.get('items_found', {})
                        })
                        # 累加 token（仅文本文件）
                        if result.get('original_tokens'):
                            self.total_orig_tokens += result['original_tokens']
                            self.total_new_tokens += result['output_tokens']
                    if self.action == 'sanitize':
                        items_found = sum(v for v in result.get('items_found', {}).values() if isinstance(v, int))
                        return (file_path.name, True, f"脱敏 {items_found}项", 0)
                    else:
                        return (file_path.name, True, "完成", saved_bytes)
                else:
                    shutil.copy2(file_path, output_path)
                    with self._lock:
                        self._processed_records.append({
                            'original': file_path.name,
                            'output': file_path.name,
                            'type': 'copy',
                            'status': 'success'
                        })
                    return (file_path.name, True, "复制", 0)

        except Exception as e:
            try:
                shutil.copy2(file_path, output_path)
                with self._lock:
                    self._processed_records.append({
                        'original': file_path.name,
                        'output': file_path.name,
                        'type': 'copy',
                        'status': 'failed',
                        'error': str(e)[:80]
                    })
                return (file_path.name, True, "复制", 0)
            except:
                with self._lock:
                    self._processed_records.append({
                        'original': file_path.name,
                        'output': '',
                        'type': self.action,
                        'status': 'failed',
                        'error': str(e)[:80]
                    })
                return (file_path.name, False, str(e), 0)

    def run(self):
        from pathlib import Path
        from concurrent.futures import ThreadPoolExecutor, as_completed

        try:
            folder = Path(self.folder)
            self._folder = folder

            if self.options.get('recursive', True):
                files = list(folder.rglob('*'))
            else:
                files = list(folder.glob('*'))

            self._files = [f for f in files if f.is_file()]
            total = len(self._files)

            workers = self.options.get('workers', 4)
            self._done_count = 0
            self._processed_records = []

            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_file = {
                    executor.submit(self._process_one, fp): fp
                    for fp in self._files
                }

                for future in as_completed(future_to_file):
                    if not self._is_running:
                        # 取消剩余任务
                        for f in future_to_file:
                            f.cancel()
                        break

                    result = future.result()
                    filename, success, message, saved_bytes = result

                    with self._lock:
                        self._done_count += 1
                        self.total_saved += saved_bytes
                        done = self._done_count

                    self.current_file.emit(filename)
                    self.file_done.emit(filename, success, message, saved_bytes)
                    self.progress.emit(done, total)

            # ========== 写入标记文件 ==========
            if self._is_running and self._processed_records:
                try:
                    from file_status import FileStatusChecker
                    checker = FileStatusChecker()

                    # 确定输出目录
                    if self.options.get('output_path'):
                        output_base = Path(self.options['output_path'])
                    elif self.options.get('backup', True):
                        output_base = folder / 'output'
                    else:
                        output_base = folder

                    checker.write_marker(
                        folder_path=str(folder),
                        processed_files=self._processed_records,
                        output_folder=str(output_base),
                        operation=self.action,
                        options=self.options
                    )
                except Exception as e:
                    print(f"[警告] 写入标记文件失败: {e}")

            if self._is_running:
                self.finished.emit()

        except Exception as e:
            self.file_done.emit("", False, f"扫描失败: {e}")
            self.finished.emit()

    def stop(self):
        self._is_running = False


class BatchTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.custom_save_location = None  # 自定义保存位置
        self.setup_ui()
        self.load_settings()

    def load_settings(self):
        """从设置文件加载默认值"""
        import json
        from pathlib import Path
        settings_file = Path(__file__).parent / 'settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # 应用设置到 UI
                self.workers_slider.setValue(settings.get('workers', 4))
                self.img_quality_slider.setValue(settings.get('image_quality', 60))
                self.text_compress_slider.setValue(settings.get('text_compression', 50))
                self.chk_remove_empty.setChecked(settings.get('remove_empty_lines', True))
            except:
                pass

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        # 文件夹选择（固定顶部）
        folder_section = self.create_folder_section()
        layout.addWidget(folder_section)

        # 可滚动内容区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(16)

        # 操作类型选择
        action_section = self.create_action_section()
        scroll_layout.addWidget(action_section)

        # 选项区域
        options_section = self.create_options_section()
        scroll_layout.addWidget(options_section)

        # 文件列表
        files_section = self.create_files_section()
        scroll_layout.addWidget(files_section, 1)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        # 进度和操作（固定底部）
        progress_section = self.create_progress_section()
        layout.addWidget(progress_section)

        # 初始化显示状态
        self.on_action_changed()

    def create_folder_section(self):
        frame = QFrame()
        frame.setObjectName("card")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)

        self.folder_label = QLabel("未选择文件夹")
        self.folder_label.setObjectName("subtitle")

        btn_browse = QPushButton("选择文件夹...")
        btn_browse.clicked.connect(self.browse_folder)

        layout.addWidget(self.folder_label)
        layout.addStretch()
        layout.addWidget(btn_browse)

        return frame

    def create_action_section(self):
        frame = QFrame()
        frame.setObjectName("card")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(24)

        title = QLabel("操作类型:")
        title.setStyleSheet("font-weight: 600;")

        self.radio_slim = QRadioButton("文档减肥")
        self.radio_slim.setChecked(True)
        self.radio_slim.toggled.connect(self.on_action_changed)

        self.radio_sanitize = QRadioButton("文档脱敏")
        self.radio_sanitize.toggled.connect(self.on_action_changed)

        # 处理模式选择
        mode_label = QLabel("处理模式:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["标准模式", "深度清理 (Word)", "转换为SSD"])
        self.mode_combo.setToolTip("标准模式：基础压缩\n深度清理：移除空段落、残留符号、非图片形状\n转换为SSD：将文档转为SSD格式")

        layout.addWidget(title)
        layout.addWidget(self.radio_slim)
        layout.addWidget(self.radio_sanitize)
        layout.addStretch()
        layout.addWidget(mode_label)
        layout.addWidget(self.mode_combo)

        return frame

    def create_options_section(self):
        frame = QFrame()
        frame.setObjectName("card")
        outer_layout = QVBoxLayout(frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # 标题
        title = QLabel("选项")
        title.setStyleSheet("font-weight: 600; font-size: 14px; padding: 16px 20px 8px 20px;")
        outer_layout.addWidget(title)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.options_scroll = scroll  # 保存引用，用于动态调整高度

        # 滚动区域内容
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 8, 20, 16)
        layout.setSpacing(12)

        # 保存位置选择
        save_layout = QHBoxLayout()
        save_label = QLabel("保存位置:")
        save_label.setStyleSheet("font-weight: 500;")

        self.save_location_label = QLabel("默认（output 子目录）")
        self.save_location_label.setObjectName("subtitle")

        btn_choose_save = QPushButton("自定义位置...")
        btn_choose_save.clicked.connect(self.choose_save_location)

        save_layout.addWidget(save_label)
        save_layout.addWidget(self.save_location_label)
        save_layout.addStretch()
        save_layout.addWidget(btn_choose_save)

        layout.addLayout(save_layout)

        # ===== 减肥模式选项（使用 QGridLayout 两列）=====
        self.slim_container = QWidget()
        slim_grid = QGridLayout(self.slim_container)
        slim_grid.setContentsMargins(8, 16, 8, 16)
        slim_grid.setHorizontalSpacing(32)
        slim_grid.setVerticalSpacing(16)
        slim_grid.setColumnStretch(0, 1)  # 左列复选框
        slim_grid.setColumnStretch(1, 2)  # 右列滑块（更宽）

        # 左列：复选框
        self.chk_recursive = QCheckBox("包含子文件夹")
        self.chk_recursive.setChecked(True)

        self.chk_backup = QCheckBox("保留原文件（输出到 output 子目录）")
        self.chk_backup.setChecked(True)

        self.chk_remove_empty = QCheckBox("移除空行")
        self.chk_remove_empty.setChecked(True)

        # 右列：滑块参数
        # 并发线程
        workers_widget = QWidget()
        workers_layout = QHBoxLayout(workers_widget)
        workers_layout.setContentsMargins(0, 0, 0, 0)
        workers_label = QLabel("并发线程:")
        workers_label.setMinimumWidth(70)
        self.workers_slider = QSlider(Qt.Orientation.Horizontal)
        self.workers_slider.setRange(1, 16)
        self.workers_slider.setValue(4)
        self.workers_slider.setMinimumHeight(24)  # 确保高度
        self.workers_value = QLabel("4")
        self.workers_value.setMinimumWidth(25)
        self.workers_slider.valueChanged.connect(lambda v: self.workers_value.setText(str(v)))
        workers_layout.addWidget(workers_label)
        workers_layout.addWidget(self.workers_slider, 1)
        workers_layout.addWidget(self.workers_value)

        # 图片质量
        img_widget = QWidget()
        img_layout = QHBoxLayout(img_widget)
        img_layout.setContentsMargins(0, 0, 0, 0)
        img_label = QLabel("图片质量:")
        img_label.setMinimumWidth(70)
        self.img_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.img_quality_slider.setRange(10, 100)
        self.img_quality_slider.setValue(60)
        self.img_quality_slider.setMinimumHeight(24)  # 确保高度
        self.img_quality_value = QLabel("60%")
        self.img_quality_value.setMinimumWidth(25)
        self.img_quality_slider.valueChanged.connect(lambda v: self.img_quality_value.setText(f"{v}%"))
        img_layout.addWidget(img_label)
        img_layout.addWidget(self.img_quality_slider, 1)
        img_layout.addWidget(self.img_quality_value)

        # 文本压缩
        text_widget = QWidget()
        text_layout = QHBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_label = QLabel("文本压缩:")
        text_label.setMinimumWidth(70)
        self.text_compress_slider = QSlider(Qt.Orientation.Horizontal)
        self.text_compress_slider.setRange(0, 100)
        self.text_compress_slider.setValue(50)
        self.text_compress_slider.setMinimumHeight(24)  # 确保高度
        self.text_compress_value = QLabel("50%")
        self.text_compress_value.setMinimumWidth(25)
        self.text_compress_slider.valueChanged.connect(lambda v: self.text_compress_value.setText(f"{v}%"))
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_compress_slider, 1)
        text_layout.addWidget(self.text_compress_value)

        # 放入网格
        slim_grid.addWidget(self.chk_recursive, 0, 0)
        slim_grid.addWidget(self.chk_backup, 1, 0)
        slim_grid.addWidget(self.chk_remove_empty, 2, 0)
        slim_grid.addWidget(workers_widget, 0, 1)
        slim_grid.addWidget(img_widget, 1, 1)
        slim_grid.addWidget(text_widget, 2, 1)
        slim_grid.setRowStretch(3, 1)

        self.slim_container.setVisible(True)  # 默认显示减肥选项
        layout.addWidget(self.slim_container)

        # ===== 脱敏模式选项 =====
        self.sanitize_container = QWidget()
        san_layout = QVBoxLayout(self.sanitize_container)
        san_layout.setContentsMargins(8, 16, 8, 16)
        san_layout.setSpacing(12)

        # 场景预设
        scene_box = QGroupBox("场景预设")
        scene_layout = QHBoxLayout(scene_box)
        scene_layout.setSpacing(16)
        self.scene_general = QRadioButton("通用文档")
        self.scene_gov = QRadioButton("党政公文")
        self.scene_finance = QRadioButton("金融合同")
        self.scene_medical = QRadioButton("医疗档案")
        self.scene_edu = QRadioButton("教育材料")
        self.scene_custom = QRadioButton("自定义")
        self.scene_general.toggled.connect(lambda: self._apply_scene('general'))
        self.scene_gov.toggled.connect(lambda: self._apply_scene('gov'))
        self.scene_finance.toggled.connect(lambda: self._apply_scene('finance'))
        self.scene_medical.toggled.connect(lambda: self._apply_scene('medical'))
        self.scene_edu.toggled.connect(lambda: self._apply_scene('edu'))
        self.scene_custom.toggled.connect(lambda: self._apply_scene('custom'))
        scene_layout.addWidget(self.scene_general)
        scene_layout.addWidget(self.scene_gov)
        scene_layout.addWidget(self.scene_finance)
        scene_layout.addWidget(self.scene_medical)
        scene_layout.addWidget(self.scene_edu)
        scene_layout.addWidget(self.scene_custom)
        scene_layout.addStretch()
        san_layout.addWidget(scene_box)

        # 基本选项
        opts_box = QGroupBox("选项")
        opts_grid = QGridLayout(opts_box)
        opts_grid.setHorizontalSpacing(16)
        self.san_chk_recursive = QCheckBox("包含子文件夹")
        self.san_chk_recursive.setChecked(True)
        self.san_chk_backup = QCheckBox("保留原文件（输出到 output 子目录）")
        self.san_chk_backup.setChecked(True)
        opts_grid.addWidget(self.san_chk_recursive, 0, 0)
        opts_grid.addWidget(self.san_chk_backup, 0, 1)
        san_layout.addWidget(opts_box)

        # 脱敏类型
        type_box = QGroupBox("脱敏类型")
        type_grid = QGridLayout(type_box)
        type_grid.setHorizontalSpacing(16)
        type_grid.setVerticalSpacing(10)

        # 第一行
        self.san_chk_phone = QCheckBox("手机号")
        self.san_chk_email = QCheckBox("邮箱")
        self.san_chk_idcard = QCheckBox("身份证")
        self.san_chk_bank = QCheckBox("银行卡")
        self.san_chk_ip = QCheckBox("IP地址")

        # 第二行
        self.san_chk_passport = QCheckBox("护照号")
        self.san_chk_mac = QCheckBox("Mac地址")
        self.san_chk_imei = QCheckBox("IMEI")
        self.san_chk_plate = QCheckBox("车牌号")
        self.san_chk_social = QCheckBox("社保卡号")

        # 第三行
        self.san_chk_credit = QCheckBox("社会信用代码")
        self.san_chk_contract = QCheckBox("合同编号")
        self.san_chk_amount = QCheckBox("投标/成交价")
        self.san_chk_license = QCheckBox("营业执照号")
        self.san_chk_phone_biz = QCheckBox("固定电话")
        # 补充缺失的 5 个类型
        self.san_chk_docnum = QCheckBox("公文份号")
        self.san_chk_doclevel = QCheckBox("密级标注")
        self.san_chk_docref = QCheckBox("公文文号")
        self.san_chk_medicare = QCheckBox("医保卡号")
        self.san_chk_medical_record = QCheckBox("病历号/门诊号")
        # 新增 6 类
        self.san_chk_account_permit = QCheckBox("开户许可证号")
        self.san_chk_purchase_order = QCheckBox("采购/订单编号")
        self.san_chk_fax = QCheckBox("传真号")
        self.san_chk_employee_id = QCheckBox("工号/学号")
        self.san_chk_project_code = QCheckBox("项目代号")
        self.san_chk_postal = QCheckBox("邮编")

        type_grid.addWidget(self.san_chk_phone, 0, 0)
        type_grid.addWidget(self.san_chk_email, 0, 1)
        type_grid.addWidget(self.san_chk_idcard, 0, 2)
        type_grid.addWidget(self.san_chk_bank, 0, 3)
        type_grid.addWidget(self.san_chk_ip, 0, 4)
        type_grid.addWidget(self.san_chk_passport, 1, 0)
        type_grid.addWidget(self.san_chk_mac, 1, 1)
        type_grid.addWidget(self.san_chk_imei, 1, 2)
        type_grid.addWidget(self.san_chk_plate, 1, 3)
        type_grid.addWidget(self.san_chk_social, 1, 4)
        type_grid.addWidget(self.san_chk_credit, 2, 0)
        type_grid.addWidget(self.san_chk_contract, 2, 1)
        type_grid.addWidget(self.san_chk_amount, 2, 2)
        type_grid.addWidget(self.san_chk_license, 2, 3)
        type_grid.addWidget(self.san_chk_phone_biz, 2, 4)
        # 第 4 行：公文/医疗相关
        type_grid.addWidget(self.san_chk_docnum, 3, 0)
        type_grid.addWidget(self.san_chk_doclevel, 3, 1)
        type_grid.addWidget(self.san_chk_docref, 3, 2)
        type_grid.addWidget(self.san_chk_medicare, 3, 3)
        type_grid.addWidget(self.san_chk_medical_record, 3, 4)
        # 第 5 行：新增 6 类
        type_grid.addWidget(self.san_chk_account_permit, 4, 0)
        type_grid.addWidget(self.san_chk_purchase_order, 4, 1)
        type_grid.addWidget(self.san_chk_fax, 4, 2)
        type_grid.addWidget(self.san_chk_employee_id, 4, 3)
        type_grid.addWidget(self.san_chk_project_code, 4, 4)
        type_grid.addWidget(self.san_chk_postal, 5, 0)

        # 全选 / 反选 按钮行
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.btn_san_select_all = QPushButton("全选")
        self.btn_san_select_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_san_select_all.clicked.connect(self._san_select_all)
        self.btn_san_deselect_all = QPushButton("反选")
        self.btn_san_deselect_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_san_deselect_all.clicked.connect(self._san_deselect_all)
        btn_row.addWidget(self.btn_san_select_all)
        btn_row.addWidget(self.btn_san_deselect_all)
        san_layout.addLayout(btn_row)

        san_layout.addWidget(type_box)

        self.sanitize_container.setVisible(False)
        layout.addWidget(self.sanitize_container)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll, 1)

        self._scene_ready = True
        # 先选中 radio，再触发场景逻辑（radio.setChecked 触发 toggled → _apply_scene）
        self.scene_general.setChecked(True)

        return frame

    def choose_save_location(self):
        """选择自定义保存位置"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择保存位置",
            ""
        )
        if folder:
            self.custom_save_location = folder
            self.save_location_label.setText(folder)
        else:
            self.custom_save_location = None
            self.save_location_label.setText("默认（output 子目录）")

    def on_action_changed(self):
        """切换操作类型"""
        if self.radio_sanitize.isChecked():
            # 显示脱敏选项
            self.slim_container.setVisible(False)
            self.sanitize_container.setVisible(True)
            self.mode_combo.setVisible(False)
        else:
            # 显示减肥选项
            self.slim_container.setVisible(True)
            self.sanitize_container.setVisible(False)
            self.mode_combo.setVisible(True)
        # 动态调整选项区域高度
        self.update_options_height()

    def get_sanitize_types(self):
        """获取选中的脱敏类型（返回字典格式）"""
        types = {}
        if self.san_chk_phone.isChecked(): types['手机号'] = True
        if self.san_chk_email.isChecked(): types['邮箱'] = True
        if self.san_chk_idcard.isChecked(): types['身份证'] = True
        if self.san_chk_bank.isChecked(): types['银行卡'] = True
        if self.san_chk_ip.isChecked(): types['IP地址'] = True
        if self.san_chk_passport.isChecked(): types['护照号'] = True
        if self.san_chk_mac.isChecked(): types['Mac地址'] = True
        if self.san_chk_imei.isChecked(): types['IMEI'] = True
        if self.san_chk_plate.isChecked(): types['车牌号'] = True
        if self.san_chk_social.isChecked(): types['社保卡号'] = True
        if self.san_chk_credit.isChecked(): types['社会信用代码'] = True
        if self.san_chk_contract.isChecked(): types['合同编号'] = True
        if self.san_chk_amount.isChecked(): types['投标/成交价'] = True
        if self.san_chk_license.isChecked(): types['营业执照号'] = True
        if self.san_chk_phone_biz.isChecked(): types['固定电话'] = True
        if self.san_chk_docnum.isChecked(): types['公文份号'] = True
        if self.san_chk_doclevel.isChecked(): types['公文密级'] = True
        if self.san_chk_docref.isChecked(): types['公文文号'] = True
        if self.san_chk_medicare.isChecked(): types['医保号'] = True
        if self.san_chk_medical_record.isChecked(): types['病历号'] = True
        if self.san_chk_account_permit.isChecked(): types['开户许可证号'] = True
        if self.san_chk_purchase_order.isChecked(): types['采购/订单编号'] = True
        if self.san_chk_fax.isChecked(): types['传真号'] = True
        if self.san_chk_employee_id.isChecked(): types['工号/学号'] = True
        if self.san_chk_project_code.isChecked(): types['项目代号'] = True
        if self.san_chk_postal.isChecked(): types['邮编'] = True
        return types

    def refresh_sanitize_types(self, types):
        """从设置标签页同步脱敏类型勾选状态"""
        type_map = {
            '手机号': 'san_chk_phone', '邮箱': 'san_chk_email', '身份证': 'san_chk_idcard',
            '银行卡': 'san_chk_bank', 'IP地址': 'san_chk_ip', '护照号': 'san_chk_passport',
            'Mac地址': 'san_chk_mac', 'IMEI': 'san_chk_imei', '车牌号': 'san_chk_plate',
            '社保卡号': 'san_chk_social', '社会信用代码': 'san_chk_credit',
            '合同编号': 'san_chk_contract', '投标/成交价': 'san_chk_amount',
            '营业执照号': 'san_chk_license', '固定电话': 'san_chk_phone_biz',
            '公文份号': 'san_chk_docnum', '公文密级': 'san_chk_doclevel',
            '公文文号': 'san_chk_docref', '医保号': 'san_chk_medicare',
            '病历号': 'san_chk_medical_record', '开户许可证号': 'san_chk_account_permit',
            '采购/订单编号': 'san_chk_purchase_order', '传真号': 'san_chk_fax',
            '工号/学号': 'san_chk_employee_id', '项目代号': 'san_chk_project_code',
            '邮编': 'san_chk_postal',
        }
        for attr in type_map.values():
            chk = getattr(self, attr, None)
            if chk:
                chk.setChecked(False)
        for t in types:
            attr = type_map.get(t)
            if attr:
                chk = getattr(self, attr, None)
                if chk:
                    chk.setChecked(True)

    def refresh_from_settings(self, settings):
        """从设置标签页同步处理参数"""
        if hasattr(self, 'workers_slider'):
            self.workers_slider.setValue(settings.get('workers', 4))
        if hasattr(self, 'img_quality_slider'):
            self.img_quality_slider.setValue(settings.get('image_quality', 60))
        if hasattr(self, 'text_compress_slider'):
            self.text_compress_slider.setValue(settings.get('text_compression', 50))

    def _san_select_all(self):
        """全选所有脱敏类型"""
        for c in [self.san_chk_phone, self.san_chk_email, self.san_chk_idcard,
                  self.san_chk_bank, self.san_chk_ip, self.san_chk_passport,
                  self.san_chk_mac, self.san_chk_imei, self.san_chk_plate,
                  self.san_chk_social, self.san_chk_credit, self.san_chk_contract,
                  self.san_chk_amount, self.san_chk_license, self.san_chk_phone_biz,
                  self.san_chk_docnum, self.san_chk_doclevel, self.san_chk_docref,
                  self.san_chk_medicare, self.san_chk_medical_record,
                  self.san_chk_account_permit, self.san_chk_purchase_order,
                  self.san_chk_fax, self.san_chk_employee_id,
                  self.san_chk_project_code, self.san_chk_postal]:
            c.setChecked(True)

    def _san_deselect_all(self):
        """反选所有脱敏类型"""
        for c in [self.san_chk_phone, self.san_chk_email, self.san_chk_idcard,
                  self.san_chk_bank, self.san_chk_ip, self.san_chk_passport,
                  self.san_chk_mac, self.san_chk_imei, self.san_chk_plate,
                  self.san_chk_social, self.san_chk_credit, self.san_chk_contract,
                  self.san_chk_amount, self.san_chk_license, self.san_chk_phone_biz,
                  self.san_chk_docnum, self.san_chk_doclevel, self.san_chk_docref,
                  self.san_chk_medicare, self.san_chk_medical_record,
                  self.san_chk_account_permit, self.san_chk_purchase_order,
                  self.san_chk_fax, self.san_chk_employee_id,
                  self.san_chk_project_code, self.san_chk_postal]:
            c.setChecked(not c.isChecked())

    def _apply_scene(self, scene: str):
        """根据场景预设联动勾选——与 settings_tab 保持完全一致"""
        if not self._scene_ready:
            return
        self._scene_ready = False  # 临时禁用，防止级联触发

        # 先全部取消勾选，再按场景勾选
        all_checks = [self.san_chk_phone, self.san_chk_email, self.san_chk_idcard,
                      self.san_chk_bank, self.san_chk_ip, self.san_chk_passport,
                      self.san_chk_mac, self.san_chk_imei, self.san_chk_plate,
                      self.san_chk_social, self.san_chk_credit, self.san_chk_contract,
                      self.san_chk_amount, self.san_chk_license, self.san_chk_phone_biz,
                      self.san_chk_docnum, self.san_chk_doclevel, self.san_chk_docref,
                      self.san_chk_medicare, self.san_chk_medical_record,
                      self.san_chk_account_permit, self.san_chk_purchase_order,
                      self.san_chk_fax, self.san_chk_employee_id,
                      self.san_chk_project_code, self.san_chk_postal]
        for c in all_checks:
            c.setChecked(False)

        # 通用文档：14 种（与 settings_tab 完全一致）
        general_items = [self.san_chk_phone, self.san_chk_email, self.san_chk_idcard,
                         self.san_chk_bank, self.san_chk_ip, self.san_chk_passport,
                         self.san_chk_mac, self.san_chk_imei, self.san_chk_plate,
                         self.san_chk_credit, self.san_chk_contract, self.san_chk_amount,
                         self.san_chk_license, self.san_chk_phone_biz,
                         self.san_chk_account_permit, self.san_chk_purchase_order,
                         self.san_chk_fax, self.san_chk_employee_id,
                         self.san_chk_project_code, self.san_chk_postal]

        if scene == 'general':
            for c in general_items:
                c.setChecked(True)
        elif scene == 'gov':
            # 通用 + 车牌 + 信用/合同/金额/执照 + 公文3件（无 mac/imei/social/phone_biz）
            for c in [self.san_chk_phone, self.san_chk_email, self.san_chk_idcard,
                      self.san_chk_bank, self.san_chk_ip, self.san_chk_passport,
                      self.san_chk_plate,
                      self.san_chk_credit, self.san_chk_contract, self.san_chk_amount,
                      self.san_chk_license,
                      self.san_chk_docnum, self.san_chk_doclevel, self.san_chk_docref]:
                c.setChecked(True)
        elif scene == 'finance':
            # 通用 + social（15种，无 phone_biz/license/公文3件/医保/病历）
            for c in [self.san_chk_phone, self.san_chk_email, self.san_chk_idcard,
                      self.san_chk_bank, self.san_chk_ip, self.san_chk_passport,
                      self.san_chk_mac, self.san_chk_imei, self.san_chk_plate,
                      self.san_chk_social, self.san_chk_credit, self.san_chk_contract,
                      self.san_chk_amount, self.san_chk_license, self.san_chk_phone_biz]:
                c.setChecked(True)
        elif scene == 'medical':
            for c in [self.san_chk_phone, self.san_chk_email, self.san_chk_idcard,
                      self.san_chk_bank, self.san_chk_ip, self.san_chk_passport,
                      self.san_chk_medicare, self.san_chk_medical_record,
                      self.san_chk_social, self.san_chk_credit, self.san_chk_contract,
                      self.san_chk_amount]:
                c.setChecked(True)
        elif scene == 'edu':
            for c in [self.san_chk_phone, self.san_chk_email, self.san_chk_idcard,
                      self.san_chk_bank, self.san_chk_ip, self.san_chk_passport,
                      self.san_chk_mac, self.san_chk_imei, self.san_chk_plate,
                      self.san_chk_credit, self.san_chk_contract, self.san_chk_amount]:
                c.setChecked(True)
        elif scene == 'custom':
            # 自定义场景：全部勾选
            for c in all_checks:
                c.setChecked(True)

        self._scene_ready = True

    def update_options_height(self):
        """根据当前模式调整选项区域显示（不再限制高度，让内容自然展开）"""
        # 移除 MaximumHeight 限制，让 QScrollArea 自然适应内容
        if hasattr(self, 'options_scroll'):
            self.options_scroll.setMaximumHeight(16777215)  # Qt.MaxInt

    def create_files_section(self):
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)

        title = QLabel("文件列表")
        title.setStyleSheet("font-weight: 600; font-size: 14px;")

        self.file_table = QTableWidget()
        self.file_table.setColumnCount(5)
        self.file_table.setHorizontalHeaderLabels(["文件名", "原大小", "新大小", "节省", "状态"])
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # 文件名
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)   # 原大小
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)   # 新大小
        self.file_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)   # 节省
        self.file_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)   # 状态
        self.file_table.setColumnWidth(1, 90)
        self.file_table.setColumnWidth(2, 90)
        self.file_table.setColumnWidth(3, 90)
        self.file_table.setColumnWidth(4, 100)
        self.file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.file_table.setAlternatingRowColors(True)

        layout.addWidget(title)
        layout.addWidget(self.file_table)

        return frame

    def create_progress_section(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # 当前正在处理的文件名
        self.file_hint_label = QLabel("")
        self.file_hint_label.setObjectName("file_hint")
        self.file_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_hint_label.setStyleSheet("color: #718096; font-size: 12px;")
        self.file_hint_label.setVisible(False)

        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_scan = QPushButton("扫描文件")
        self.btn_scan.setEnabled(False)
        self.btn_scan.clicked.connect(self.scan_files)

        self.btn_start = QPushButton("开始处理")
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.start_processing)

        self.btn_stop = QPushButton("停止")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_processing)

        btn_layout.addWidget(self.btn_scan)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.file_hint_label)
        layout.addWidget(self.status_label)
        layout.addLayout(btn_layout)

        return frame

    def set_folder(self, folder_path):
        """设置文件夹（供拖拽使用）"""
        self.folder_label.setText(folder_path)
        self.btn_scan.setEnabled(True)
        self.scan_files()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_label.setText(folder)
            self.btn_scan.setEnabled(True)
            self.scan_files()

    def scan_files(self):
        """扫描文件夹中的文件"""
        folder = self.folder_label.text()
        if folder == "未选择文件夹":
            return

        from pathlib import Path

        supported_extensions = {
            '.txt', '.md', '.json', '.csv', '.xml', '.html',
            '.docx', '.xlsx', '.xls', '.pptx', '.pdf',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'
        }

        try:
            folder_path = Path(folder)
            files = []

            # 根据当前模式选择对应的递归选项
            if self.radio_sanitize.isChecked():
                recursive = self.san_chk_recursive.isChecked()
            else:
                recursive = self.chk_recursive.isChecked()

            # 扫描所有文件（不只是支持的格式）
            if recursive:
                files = list(folder_path.rglob('*'))
            else:
                files = list(folder_path.glob('*'))

            # 过滤掉目录
            files = [f for f in files if f.is_file()]

            self.file_table.setRowCount(len(files))

            for i, f in enumerate(files):
                self.file_table.setItem(i, 0, QTableWidgetItem(f.name))
                size_str = self.format_size(f.stat().st_size)
                self.file_table.setItem(i, 1, QTableWidgetItem(size_str))
                self.file_table.setItem(i, 2, QTableWidgetItem("-"))
                self.file_table.setItem(i, 3, QTableWidgetItem("-"))
                self.file_table.setItem(i, 4, QTableWidgetItem("待处理"))

            self.status_label.setText(f"找到 {len(files)} 个文件")
            self.btn_start.setEnabled(len(files) > 0)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"扫描失败: {e}")

    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def start_processing(self):
        """开始批量处理"""
        folder = self.folder_label.text()
        if folder == "未选择文件夹":
            return

        action = 'slim' if self.radio_slim.isChecked() else 'sanitize'

        # 根据操作类型选择对应的选项
        if action == 'slim':
            recursive = self.chk_recursive.isChecked()
            backup = self.chk_backup.isChecked()
        else:
            recursive = self.san_chk_recursive.isChecked()
            backup = self.san_chk_backup.isChecked()

        options = {
            'recursive': recursive,
            'backup': backup,
            'remove_empty': self.chk_remove_empty.isChecked(),
            'deep_clean': self.mode_combo.currentText() == "深度清理 (Word)",
            'convert_to_ssd': self.mode_combo.currentText() == "转换为SSD",
            'compression_rate': self.text_compress_slider.value() / 100.0,
            'output_path': self.custom_save_location,
            'image_quality': self.img_quality_slider.value(),
            'workers': self.workers_slider.value(),
        }

        if action == 'sanitize':
            sanitize_items = self.get_sanitize_types()
            options['sanitize_items'] = sanitize_items
            print(f"[DEBUG batch_tab] action=sanitize, sanitize_items={list(sanitize_items.keys()) if sanitize_items else 'EMPTY'}")

        print(f"[DEBUG batch_tab] convert_to_ssd={options.get('convert_to_ssd')}, mode_combo={self.mode_combo.currentText()}")

        # ========== 处理前状态检测（主线程弹窗）==========
        try:
            from file_status import FileStatusChecker, get_user_friendly_message
            from PyQt6.QtWidgets import QMessageBox
            checker = FileStatusChecker()
            pre_check = checker.check_folder(folder, action=action)
            status = pre_check.get('status', 'UNPROCESSED')
            details = pre_check.get('details', {})
            action_name = '脱敏' if action == 'sanitize' else '减肥'

            if status == 'PROCESSED':
                stats = details.get('stats', {})
                total = stats.get('total', details.get('total', 0))
                success = stats.get('success', details.get('processed', 0))
                copied = stats.get('copied', details.get('copied', 0))

                msg = f"该文件夹已进行过{action_name}处理"
                if success > 0:
                    msg += f"（{success} 个文件"
                    if action_name == '脱敏':
                        files = details.get('files', [])
                        total_items = 0
                        for f in files:
                            items = f.get('items_found', {})
                            if isinstance(items, dict):
                                total_items += sum(v for v in items.values() if isinstance(v, int))
                        if total_items > 0:
                            msg += f"，共脱敏 {total_items} 项"
                        msg += "）"
                    else:
                        msg += "）"
                if copied > 0:
                    msg += f"，{copied} 个文件直接复制"
                msg += "。\n\n是否重新处理？"

                reply = QMessageBox.question(
                    self,
                    f"已{action_name}过",
                    msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return  # 用户选择不重新处理，直接返回

            elif status == 'PARTIAL':
                processed = details.get('processed', 0)
                unprocessed = details.get('unprocessed', 0)
                msg = f"该文件夹中已有 {processed} 个文件进行过{action_name}，{unprocessed} 个文件尚未处理。\n\n是否继续处理剩余文件？"
                reply = QMessageBox.question(
                    self,
                    f"部分已{action_name}",
                    msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.No:
                    return

        except ImportError:
            pass  # 检测模块不可用，直接继续

        # ========== 启动 Worker ==========
        self.worker = BatchWorker(folder, action, options)
        self.worker.progress.connect(self.update_progress)
        self.worker.current_file.connect(self.on_current_file)
        self.worker.file_done.connect(self.on_file_done)
        self.worker.finished.connect(self.on_finished)

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.file_hint_label.setText("正在处理...")
        self.file_hint_label.setStyleSheet("color: #718096; font-size: 12px;")
        self.file_hint_label.setVisible(True)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self.worker.start()

    def update_progress(self, current, total):
        """更新进度"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"处理中... {current}/{total}")

    def on_current_file(self, filename):
        """当前开始处理的文件名"""
        self.file_hint_label.setText(f"正在处理：{filename}")
        self.file_hint_label.setVisible(True)

    def on_file_done(self, filename, success, message, saved_bytes):
        """单个文件处理完成"""
        # 在表格中找到对应的行并更新状态
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, 0)
            if item and item.text() == filename:
                # 判断是脱敏模式还是减肥模式
                is_sanitize = "脱敏" in message

                if is_sanitize:
                    # 脱敏模式：第3列显示节省，第4列显示状态
                    self.file_table.setItem(row, 2, QTableWidgetItem("-"))  # 新大小
                    self.file_table.setItem(row, 3, QTableWidgetItem("-"))  # 节省
                    status_item = QTableWidgetItem(f"✓ {message}")
                    status_item.setForeground(Qt.GlobalColor.green)
                    self.file_table.setItem(row, 4, status_item)  # 状态
                else:
                    # 减肥模式：第3列显示节省，第4列显示状态
                    if success:
                        if saved_bytes > 0:
                            saved_str = f"↓ {self.format_size(saved_bytes)}"
                            saved_item = QTableWidgetItem(saved_str)
                            saved_item.setForeground(Qt.GlobalColor.green)
                        elif saved_bytes < 0:
                            saved_str = f"↑ {self.format_size(abs(saved_bytes))}"
                            saved_item = QTableWidgetItem(saved_str)
                            saved_item.setForeground(Qt.GlobalColor.red)
                        else:
                            saved_item = QTableWidgetItem("-")
                        self.file_table.setItem(row, 3, saved_item)
                        status_item = QTableWidgetItem(f"✓ 完成")
                        status_item.setForeground(Qt.GlobalColor.green)
                    else:
                        self.file_table.setItem(row, 3, QTableWidgetItem("-"))
                        status_item = QTableWidgetItem(f"✗ {message}")
                        status_item.setForeground(Qt.GlobalColor.red)
                    self.file_table.setItem(row, 4, status_item)
                break

    def on_finished(self):
        """全部处理完成"""
        try:
            self.progress_bar.setVisible(False)
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)

            # 显示输出目录
            folder = self.folder_label.text()
            if folder != "未选择文件夹":
                output_dir = Path(folder) / 'output'
                self.status_label.setText(f"处理完成，输出目录: {output_dir}")
            else:
                self.status_label.setText("处理完成")

            self.file_hint_label.setVisible(False)

            # 显示批量处理结果对比
            self.show_batch_compare(folder)
        except Exception as e:
            print(f"[ERROR] on_finished 异常: {e}")
            import traceback
            traceback.print_exc()

    def show_batch_compare(self, folder=None):
        """显示批量处理结果对比"""
        from result_compare_dialog import ResultCompareDialog

        # 统计结果
        total_files = self.file_table.rowCount()
        success_count = 0
        total_items = 0  # 脱敏处数

        for row in range(total_files):
            # 脱敏模式状态在第4列，减肥模式状态在第2列
            status_col2 = self.file_table.item(row, 2)
            status_col4 = self.file_table.item(row, 4)
            status_text = ""
            if status_col4 and ("脱敏" in status_col4.text() or "完成" in status_col4.text()):
                status_text = status_col4.text()
            elif status_col2 and ("完成" in status_col2.text() or "脱敏" in status_col2.text()):
                status_text = status_col2.text()

            if status_text and ("完成" in status_text or "脱敏" in status_text):
                success_count += 1
                # 解析脱敏处数
                if "脱敏" in status_text:
                    try:
                        items = int(status_text.split("脱敏")[1].split("项")[0].strip())
                        total_items += items
                    except:
                        pass

        # 获取当前操作类型
        action = 'slim' if self.radio_slim.isChecked() else 'sanitize'

        # 直接从 worker 获取总节省空间（仅减肥模式）
        total_saved = self.worker.total_saved if self.worker else 0

        print(f"[DEBUG] 总节省: {total_saved} bytes = {self.format_size(total_saved)}")

        # 关键：用 window() 获取真正的顶级窗口作为父，避免对话框关闭时误关主窗口
        main_win = self.window()
        dialog = ResultCompareDialog(main_win)

        if action == 'sanitize':
            # 脱敏模式：显示脱敏处数
            dialog.set_batch_result(
                total_files,
                success_count,
                total_items,
                [],
                action='sanitize'
            )
        else:
            # 减肥模式：显示节省空间 + Token
            dialog.set_batch_result(
                total_files,
                success_count,
                total_saved,
                [],
                action='slim',
                original_tokens=self.worker.total_orig_tokens if self.worker else 0,
                new_tokens=self.worker.total_new_tokens if self.worker else 0
            )

        # 显示对话框，捕获任何异常防止软件退出
        try:
            dialog.exec()
        except Exception as e:
            print(f"[ERROR] 结果对话框异常: {e}")

        # 保存到历史
        self.save_batch_to_history(total_files, success_count, total_saved, folder, action, total_items)

    def save_batch_to_history(self, total_files, success_count, total_saved, folder_path, action='slim', total_items=0):
        """保存批量处理到历史"""
        try:
            # 从表格计算总原大小和总新大小
            total_orig_size = 0
            total_new_size = 0

            for row in range(self.file_table.rowCount()):
                # 获取原大小（第2列）
                orig_item = self.file_table.item(row, 1)
                orig_size = 0
                if orig_item:
                    orig_size = self.parse_size(orig_item.text())
                    total_orig_size += orig_size  # 累加到总原大小

                # 获取状态，判断是否成功
                status_col2 = self.file_table.item(row, 2)
                status_col4 = self.file_table.item(row, 4)
                is_success = (
                    (status_col4 and ("脱敏" in status_col4.text() or "完成" in status_col4.text())) or
                    (status_col2 and ("完成" in status_col2.text() or "脱敏" in status_col2.text()))
                )
                if is_success:
                    # 成功处理，新大小 = 该行原大小 - 节省
                    saved_item = self.file_table.item(row, 3)
                    if saved_item and saved_item.text() != "-":
                        saved_text = saved_item.text().replace("↓ ", "").replace("↑ ", "")
                        saved_size = self.parse_size(saved_text)
                        total_new_size += orig_size - saved_size
                    else:
                        total_new_size += orig_size
                else:
                    # 未处理或失败，新大小 = 原大小
                    total_new_size += total_orig_size

            main_window = self.window()
            print(f"[DEBUG] save_history: main_window={type(main_window).__name__}, has_manager={hasattr(main_window, 'history_manager')}, has_tab={hasattr(main_window, 'tab_history')}")
            if hasattr(main_window, 'history_manager'):
                # 计算节省百分比
                if action == 'slim':
                    saved_percent = round((1 - total_new_size/total_orig_size) * 100, 1) if total_orig_size > 0 else 0
                else:
                    saved_percent = 0
                    total_saved = 0  # 脱敏模式不计算节省空间

                # 创建批量处理记录
                record = {
                    'id': __import__('datetime').datetime.now().strftime('%Y%m%d%H%M%S'),
                    'time': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'file_name': f'批量处理 ({total_files}个文件)',
                    'file_path': folder_path,
                    'action': action,
                    'original_size': total_orig_size,
                    'new_size': total_new_size,
                    'saved_size': total_saved,
                    'saved_percent': saved_percent,
                    'output_path': None,
                    'batch': True,
                    'total_files': total_files,
                    'success_count': success_count,
                    'total_items': total_items,  # 脱敏总处数
                    'original_tokens': self.worker.total_orig_tokens if self.worker else None,
                    'new_tokens': self.worker.total_new_tokens if self.worker else None,
                }
                print(f"[DEBUG] save_history: appending record, history len before={len(main_window.history_manager.history)}")
                main_window.history_manager.history.append(record)
                main_window.history_manager.save_history()
                print(f"[DEBUG] save_history: history len after={len(main_window.history_manager.history)}")
                if hasattr(main_window, 'tab_history'):
                    print(f"[DEBUG] save_history: calling load_history")
                    main_window.tab_history.load_history()
        except Exception as e:
            print(f"保存历史失败: {e}")

    def parse_size(self, size_text):
        """解析大小字符串为字节数"""
        if not size_text or size_text == "-":
            return 0
        try:
            size_text = size_text.strip()
            if "KB" in size_text:
                return float(size_text.replace("KB", "").strip()) * 1024
            elif "MB" in size_text:
                return float(size_text.replace("MB", "").strip()) * 1024 * 1024
            elif "GB" in size_text:
                return float(size_text.replace("GB", "").strip()) * 1024 * 1024 * 1024
            elif "B" in size_text:
                return float(size_text.replace("B", "").strip())
            else:
                return 0
        except:
            return 0

    def stop_processing(self):
        """停止处理"""
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        self.btn_stop.setEnabled(False)
        self.btn_start.setEnabled(True)
        self.status_label.setText("已停止")
        self.file_hint_label.setVisible(False)

    def cleanup(self):
        """清理资源"""
        if self.worker:
            self.worker.stop()
            self.worker.wait()
    
    def update_language(self, lang):
        """更新语言"""
        from translations import get_translation
        _ = lambda t: get_translation(t, lang)
        
        # 更新操作类型
        if hasattr(self, 'radio_slim'):
            self.radio_slim.setText(_('文档减肥'))
        if hasattr(self, 'radio_sanitize'):
            self.radio_sanitize.setText(_('文档脱敏'))
        
        # 更新处理模式
        if hasattr(self, 'mode_combo'):
            items = [_('标准模式'), _('深度清理 (Word)'), _('转换为SSD')]
            self.mode_combo.clear()
            self.mode_combo.addItems(items)
        
        # 更新场景预设
        if hasattr(self, 'scene_general'):
            self.scene_general.setText(_('通用文档'))
        if hasattr(self, 'scene_gov'):
            self.scene_gov.setText(_('党政公文'))
        if hasattr(self, 'scene_finance'):
            self.scene_finance.setText(_('金融合同'))
        if hasattr(self, 'scene_medical'):
            self.scene_medical.setText(_('医疗档案'))
        if hasattr(self, 'scene_edu'):
            self.scene_edu.setText(_('教育材料'))
        if hasattr(self, 'scene_custom'):
            self.scene_custom.setText(_('自定义'))
        
        # 更新复选框
        if hasattr(self, 'chk_recursive'):
            self.chk_recursive.setText(_('包含子文件夹'))
        if hasattr(self, 'chk_backup'):
            self.chk_backup.setText(_('保留原文件（输出到 output 子目录）'))
        if hasattr(self, 'chk_remove_empty'):
            self.chk_remove_empty.setText(_('移除空行'))
        
        # 更新按钮
        if hasattr(self, 'btn_scan'):
            self.btn_scan.setText(_('扫描文件'))
        if hasattr(self, 'btn_start'):
            self.btn_start.setText(_('开始处理'))
        if hasattr(self, 'btn_stop'):
            self.btn_stop.setText(_('停止'))
        
        # 更新表格标题
        if hasattr(self, 'file_table'):
            self.file_table.setHorizontalHeaderLabels([
                _('文件名'), _('原大小'), _('新大小'), _('节省'), _('状态')
            ])
