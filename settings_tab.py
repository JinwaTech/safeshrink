# -*- coding: utf-8 -*-
"""
设置标签页
功能：集中管理所有配置项
优化：分组清晰、标签对齐、间距合理
"""

import json
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QSpinBox, QCheckBox,
    QFrame, QGroupBox, QFileDialog, QLineEdit,
    QComboBox, QTabWidget, QScrollArea, QSizePolicy,
    QRadioButton
)
from PySide6.QtCore import Qt, Signal

class AutoFitScrollArea(QScrollArea):
    """自动适配视口宽度的 ScrollArea，内容区宽度跟随窗口，内核滚动条正确触发"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        # 强制 viewport 背景跟随主题，避免默认白色底色
        self.viewport().setAutoFillBackground(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.viewport().width()
        if w > 0 and self.widget() is not None:
            self.widget().setMinimumWidth(w)

# 默认配置
DEFAULT_SETTINGS = {
    'language': 'zh-CN',
    'theme': 'light',
    'auto_check_update': True,
    'minimize_to_tray': False,
    'confirm_on_exit': True,
    'output_dir': '',
    'auto_backup': True,
    'overwrite_confirm': True,
    'preserve_structure': True,
    'timestamp_output': False,
    'workers': 4,
    'image_quality': 60,
    'text_compression': 50,
    'pdf_quality': 70,
    'remove_empty_lines': True,
    'remove_empty_paragraphs': True,
    'deep_clean_word': False,
    'embed_images': True,
    'sanitize_types': ['手机号', '邮箱', '身份证', '银行卡', 'IP地址', '护照号', 'Mac地址', 'IMEI', '车牌号', '社保卡号', '社会信用代码', '合同编号', '投标/成交价', '营业执照号', '固定电话', '公文份号', '公文密级', '公文文号', '医保号', '病历号'],
    'mask_char': '*',
    'preserve_first_last': True,
    'sanitize_mode': 'mask',
    'history_limit': 100,
    'show_result_dialog': True,
    'show_progress_detail': True,
    'font_size': 14,
    'table_row_height': 32,
    'log_level': 'info',
    'max_log_size_mb': 10,
    'cache_enabled': True,
    'cache_size_mb': 100,
}


def _get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path.home() / 'AppData' / 'Roaming' / 'SafeShrink'
    return Path(__file__).parent


class SettingsTab(QWidget):
    settings_changed = Signal(dict)  # 设置变更信号，通知其他标签页刷新

    def __init__(self, parent=None):
        super().__init__()
        self.settings_file = _get_base_dir() / 'settings.json'
        self.settings = self.load_settings()
        self.theme_callback = None
        self._main_window = None  # 由 MainWindow 注入，用于访问其他标签页
        self.setup_ui()

    def load_settings(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    settings = DEFAULT_SETTINGS.copy()
                    settings.update(saved)
                    return settings
            except:
                return DEFAULT_SETTINGS.copy()
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

    def set_theme_callback(self, callback):
        self.theme_callback = callback

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 0)  # bottom=0，消除白线间隙
        title = QLabel("设置")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addWidget(header)

        # 标签页容器
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setProperty("drawBase", False)
        tabs.tabBar().setDrawBase(False)
        tabs.addTab(self.create_general_tab(), "通用")
        tabs.addTab(self.create_output_tab(), "输出")
        tabs.addTab(self.create_process_tab(), "处理")
        tabs.addTab(self.create_sanitize_tab(), "脱敏")
        tabs.addTab(self.create_ui_tab(), "界面")
        tabs.addTab(self.create_advanced_tab(), "高级")

        layout.addWidget(tabs, 1)

        # 底部按钮
        btn_frame = QFrame()
        btn_frame.setObjectName("card")
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(24, 12, 24, 12)

        self.btn_reset = QPushButton("恢复默认")
        self.btn_reset.setProperty("secondary", True)
        self.btn_reset.clicked.connect(self.on_reset)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset)

        self.btn_save = QPushButton("保存设置")
        self.btn_save.clicked.connect(self.on_save)
        btn_layout.addWidget(self.btn_save)

        layout.addWidget(btn_frame)

    def create_row(self, label_text, widget, hint_text=None):
        """创建一行设置项：标签 + 控件 + 提示"""
        layout = QHBoxLayout()
        layout.setSpacing(16)

        label = QLabel(label_text)
        label.setMinimumWidth(140)
        label.setStyleSheet("font-weight: 500;")

        layout.addWidget(label)
        if widget:
            layout.addWidget(widget, 1)

        if hint_text:
            hint = QLabel(hint_text)
            hint.setProperty("class", "hint-text")
            layout.addWidget(hint)

        return layout

    def create_separator(self):
        """创建分隔线 - 样式由 theme_manager 统一控制"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("divider")
        return line

    # ===== 通用设置 =====
    def create_general_tab(self):
        scroll = AutoFitScrollArea()

        scroll.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        widget.setMinimumWidth(800)  # 初始值，resizeEvent 会动态修正

        # 外观设置
        group1 = QGroupBox("外观")
        g1_layout = QVBoxLayout(group1)
        g1_layout.setSpacing(16)

        # 语言
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['简体中文', 'English'])
        self.lang_combo.setCurrentIndex(0 if self.settings.get('language') == 'zh-CN' else 1)
        self.lang_combo.setMinimumWidth(150)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)  # ← 新增
        g1_layout.addLayout(self.create_row("语言", self.lang_combo))

        # 主题
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['浅色', '深色', '跟随系统'])
        theme_idx = {'light': 0, 'dark': 1, 'system': 2}
        self.theme_combo.setCurrentIndex(theme_idx.get(self.settings.get('theme'), 1))
        self.theme_combo.setMinimumWidth(150)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        g1_layout.addLayout(self.create_row("颜色主题", self.theme_combo))

        layout.addWidget(group1)

        # 启动与退出
        group2 = QGroupBox("启动与退出")
        g2_layout = QVBoxLayout(group2)
        g2_layout.setSpacing(12)

        self.chk_auto_update = QCheckBox("启动时自动检查更新")
        self.chk_auto_update.setChecked(self.settings.get('auto_check_update', True))
        g2_layout.addWidget(self.chk_auto_update)

        self.chk_minimize_tray = QCheckBox("最小化到系统托盘")
        self.chk_minimize_tray.setChecked(self.settings.get('minimize_to_tray', False))
        g2_layout.addWidget(self.chk_minimize_tray)

        self.chk_confirm_exit = QCheckBox("退出时确认")
        self.chk_confirm_exit.setChecked(self.settings.get('confirm_on_exit', True))
        g2_layout.addWidget(self.chk_confirm_exit)

        layout.addWidget(group2)
        scroll.setWidget(widget)
        return scroll

    # ===== 输出设置 =====
    def create_output_tab(self):
        scroll = AutoFitScrollArea()

        scroll.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        widget.setMinimumWidth(800)  # 初始值，resizeEvent 会动态修正

        # 输出位置
        group1 = QGroupBox("输出位置")
        g1_layout = QVBoxLayout(group1)
        g1_layout.setSpacing(16)

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("留空则保存到 output 子目录")
        self.output_dir_edit.setText(self.settings.get('output_dir', ''))
        btn_browse = QPushButton("浏览...")
        btn_browse.setProperty("secondary", True)
        btn_browse.clicked.connect(self.browse_output_dir)
        btn_browse.setFixedWidth(80)

        dir_row = QHBoxLayout()
        dir_row.addWidget(self.output_dir_edit, 1)
        dir_row.addWidget(btn_browse)
        g1_layout.addLayout(self.create_row("默认目录", None))
        g1_layout.addLayout(dir_row)

        layout.addWidget(group1)

        # 输出选项
        group2 = QGroupBox("输出选项")
        g2_layout = QVBoxLayout(group2)
        g2_layout.setSpacing(12)

        self.chk_auto_backup = QCheckBox("默认保留原文件")
        self.chk_auto_backup.setChecked(self.settings.get('auto_backup', True))
        g2_layout.addWidget(self.chk_auto_backup)

        self.chk_overwrite_confirm = QCheckBox("覆盖文件前确认")
        self.chk_overwrite_confirm.setChecked(self.settings.get('overwrite_confirm', True))
        g2_layout.addWidget(self.chk_overwrite_confirm)

        self.chk_preserve_structure = QCheckBox("保留原始文件夹结构")
        self.chk_preserve_structure.setChecked(self.settings.get('preserve_structure', True))
        g2_layout.addWidget(self.chk_preserve_structure)

        self.chk_timestamp = QCheckBox("输出文件名添加时间戳")
        self.chk_timestamp.setChecked(self.settings.get('timestamp_output', False))
        g2_layout.addWidget(self.chk_timestamp)

        layout.addWidget(group2)
        scroll.setWidget(widget)
        return scroll

    # ===== 处理设置 =====
    def create_process_tab(self):
        scroll = AutoFitScrollArea()

        scroll.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        widget.setMinimumWidth(800)  # 初始值，resizeEvent 会动态修正

        # 性能设置
        group1 = QGroupBox("性能")
        g1_layout = QVBoxLayout(group1)
        g1_layout.setSpacing(16)

        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 16)
        self.workers_spin.setValue(self.settings.get('workers', 4))
        self.workers_spin.setFixedWidth(80)
        g1_layout.addLayout(self.create_row("并发线程数", self.workers_spin, "小文件 4-8，大文件 1-4"))

        layout.addWidget(group1)

        # 压缩质量
        group2 = QGroupBox("压缩质量")
        g2_layout = QVBoxLayout(group2)
        g2_layout.setSpacing(20)

        # 图片压缩
        img_row = QHBoxLayout()
        img_label = QLabel("图片质量")
        img_label.setMinimumWidth(140)
        img_label.setStyleSheet("font-weight: 500;")
        self.img_slider = QSlider(Qt.Orientation.Horizontal)
        self.img_slider.setRange(10, 100)
        self.img_slider.setValue(self.settings.get('image_quality', 60))
        self.img_value = QLabel(f"{self.settings.get('image_quality', 60)}%")
        self.img_value.setMinimumWidth(50)
        self.img_slider.valueChanged.connect(lambda v: self.img_value.setText(f"{v}%"))
        img_row.addWidget(img_label)
        img_row.addWidget(self.img_slider, 1)
        img_row.addWidget(self.img_value)
        g2_layout.addLayout(img_row)

        # 文本压缩
        text_row = QHBoxLayout()
        text_label = QLabel("文本压缩")
        text_label.setMinimumWidth(140)
        text_label.setStyleSheet("font-weight: 500;")
        self.text_slider = QSlider(Qt.Orientation.Horizontal)
        self.text_slider.setRange(0, 100)
        self.text_slider.setValue(self.settings.get('text_compression', 50))
        self.text_value = QLabel(f"{self.settings.get('text_compression', 50)}%")
        self.text_value.setMinimumWidth(50)
        self.text_slider.valueChanged.connect(lambda v: self.text_value.setText(f"{v}%"))
        text_row.addWidget(text_label)
        text_row.addWidget(self.text_slider, 1)
        text_row.addWidget(self.text_value)
        g2_layout.addLayout(text_row)

        # PDF 质量
        pdf_row = QHBoxLayout()
        pdf_label = QLabel("PDF 质量")
        pdf_label.setMinimumWidth(140)
        pdf_label.setStyleSheet("font-weight: 500;")
        self.pdf_slider = QSlider(Qt.Orientation.Horizontal)
        self.pdf_slider.setRange(10, 100)
        self.pdf_slider.setValue(self.settings.get('pdf_quality', 70))
        self.pdf_value = QLabel(f"{self.settings.get('pdf_quality', 70)}%")
        self.pdf_value.setMinimumWidth(50)
        self.pdf_slider.valueChanged.connect(lambda v: self.pdf_value.setText(f"{v}%"))
        pdf_row.addWidget(pdf_label)
        pdf_row.addWidget(self.pdf_slider, 1)
        pdf_row.addWidget(self.pdf_value)
        g2_layout.addLayout(pdf_row)

        layout.addWidget(group2)

        # 清理选项
        group3 = QGroupBox("清理选项")
        g3_layout = QVBoxLayout(group3)
        g3_layout.setSpacing(12)

        self.chk_remove_empty = QCheckBox("移除空行")
        self.chk_remove_empty.setChecked(self.settings.get('remove_empty_lines', True))
        g3_layout.addWidget(self.chk_remove_empty)

        self.chk_remove_empty_para = QCheckBox("移除空段落 (Word)")
        self.chk_remove_empty_para.setChecked(self.settings.get('remove_empty_paragraphs', True))
        g3_layout.addWidget(self.chk_remove_empty_para)

        self.chk_deep_clean = QCheckBox("Word 深度清理（移除隐藏元数据）")
        self.chk_deep_clean.setChecked(self.settings.get('deep_clean_word', False))
        g3_layout.addWidget(self.chk_deep_clean)

        self.chk_embed = QCheckBox("SSD 转换时嵌入图片（Base64）")
        self.chk_embed.setChecked(self.settings.get('embed_images', True))
        self.chk_embed.setToolTip("勾选：图片转为Base64内嵌，SSD为单文件但体积变大\n不勾选：只保留文字引用，文件更小（推荐）")
        g3_layout.addWidget(self.chk_embed)

        layout.addWidget(group3)
        scroll.setWidget(widget)
        return scroll

    # ===== 脱敏设置 =====
    def create_sanitize_tab(self):
        scroll = AutoFitScrollArea()

        scroll.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        widget.setMinimumWidth(800)  # 初始值，resizeEvent 会动态修正

        # 场景预设
        scene_group = QGroupBox("适用场景（快捷预设）")
        sg_layout = QVBoxLayout(scene_group)
        sg_layout.setSpacing(8)

        scene_tip = QLabel("选择场景后自动勾选对应脱敏类型，可手动调整")
        scene_tip.setStyleSheet("color: #8b92a5; font-size: 12px;")
        sg_layout.addWidget(scene_tip)

        scene_row = QHBoxLayout()
        self.scene_general = QRadioButton("通用文档（推荐）")
        self.scene_general.setChecked(True)
        self.scene_gov = QRadioButton("党政公文")
        self.scene_finance = QRadioButton("金融合同")
        self.scene_medical = QRadioButton("医疗档案")
        self.scene_edu = QRadioButton("教育材料")
        scene_row.addWidget(self.scene_general)
        scene_row.addWidget(self.scene_gov)
        scene_row.addWidget(self.scene_finance)
        scene_row.addWidget(self.scene_medical)
        scene_row.addWidget(self.scene_edu)

        # 自定义场景：默认全部勾选
        self.scene_custom = QRadioButton("自定义")
        self.scene_custom.setToolTip("自定义脱敏项组合，默认全部勾选")
        self.scene_custom.toggled.connect(lambda: self._apply_scene('custom'))
        scene_row.addWidget(self.scene_custom)

        scene_row.addStretch()
        sg_layout.addLayout(scene_row)

        # 场景联动在 UI 全部创建后再启用（_scene_ready 标志位）
        self._scene_ready = False
        self.scene_general.toggled.connect(lambda: self._apply_scene('general'))
        self.scene_gov.toggled.connect(lambda: self._apply_scene('gov'))
        self.scene_finance.toggled.connect(lambda: self._apply_scene('finance'))
        self.scene_medical.toggled.connect(lambda: self._apply_scene('medical'))
        self.scene_edu.toggled.connect(lambda: self._apply_scene('edu'))

        layout.addWidget(scene_group)

        # 默认脱敏类型
        group1 = QGroupBox("默认脱敏类型")
        g1_layout = QVBoxLayout(group1)
        g1_layout.setSpacing(12)

        types = self.settings.get('sanitize_types', ['手机号', '邮箱', '身份证', '银行卡', 'IP地址'])

        # 个人敏感信息
        personal_label = QLabel("个人敏感:")
        personal_label.setStyleSheet("font-size: 12px; color: #8b92a5; margin-top: 4px;")
        g1_layout.addWidget(personal_label)

        self.chk_phone = QCheckBox("手机号 (138****8888)")
        self.chk_phone.setChecked('手机号' in types)
        g1_layout.addWidget(self.chk_phone)

        self.chk_email = QCheckBox("邮箱 (ab***@domain.com)")
        self.chk_email.setChecked('邮箱' in types)
        g1_layout.addWidget(self.chk_email)

        self.chk_idcard = QCheckBox("身份证号 (3301***********4)")
        self.chk_idcard.setChecked('身份证' in types)
        g1_layout.addWidget(self.chk_idcard)

        self.chk_bankcard = QCheckBox("银行卡号 (1234****5678)")
        self.chk_bankcard.setChecked('银行卡' in types)
        g1_layout.addWidget(self.chk_bankcard)

        self.chk_ip = QCheckBox("IP 地址 (xxx.xxx.xxx.xxx)")
        self.chk_ip.setChecked('IP地址' in types)
        g1_layout.addWidget(self.chk_ip)

        self.chk_passport = QCheckBox("护照号 (G********1)")
        self.chk_passport.setChecked('护照号' in types)
        g1_layout.addWidget(self.chk_passport)

        self.chk_mac = QCheckBox("Mac 地址 (AA:BB:CC:**:**:**)")
        self.chk_mac.setChecked('Mac地址' in types)
        g1_layout.addWidget(self.chk_mac)

        self.chk_imei = QCheckBox("IMEI 设备号 (460012******34)")
        self.chk_imei.setChecked('IMEI' in types)
        g1_layout.addWidget(self.chk_imei)

        self.chk_plate = QCheckBox("车牌号 (浙A*****5)")
        self.chk_plate.setChecked('车牌号' in types)
        g1_layout.addWidget(self.chk_plate)

        self.chk_social = QCheckBox("社保卡号 (330***********4)")
        self.chk_social.setChecked('社保卡号' in types)
        g1_layout.addWidget(self.chk_social)

        # 商业敏感信息
        biz_label = QLabel("商业敏感:")
        biz_label.setStyleSheet("font-size: 12px; color: #8b92a5; margin-top: 8px;")
        g1_layout.addWidget(biz_label)

        self.chk_credit = QCheckBox("社会信用代码 (91**********)")
        self.chk_credit.setChecked('社会信用代码' in types)
        g1_layout.addWidget(self.chk_credit)

        self.chk_contract = QCheckBox("合同编号 (HT-****-2024)")
        self.chk_contract.setChecked('合同编号' in types)
        g1_layout.addWidget(self.chk_contract)

        self.chk_amount = QCheckBox("投标/成交价 (¥***万)")
        self.chk_amount.setChecked('投标/成交价' in types)
        g1_layout.addWidget(self.chk_amount)

        self.chk_license = QCheckBox("营业执照号 (9135********)")
        self.chk_license.setChecked('营业执照号' in types)
        g1_layout.addWidget(self.chk_license)

        self.chk_phone_biz = QCheckBox("固定电话 (0571-****8888)")
        self.chk_phone_biz.setChecked('固定电话' in types)
        g1_layout.addWidget(self.chk_phone_biz)

        self.chk_account_permit = QCheckBox("开户许可证号")
        self.chk_account_permit.setChecked('开户许可证号' in types)
        g1_layout.addWidget(self.chk_account_permit)

        self.chk_purchase_order = QCheckBox("采购/订单编号")
        self.chk_purchase_order.setChecked('采购/订单编号' in types)
        g1_layout.addWidget(self.chk_purchase_order)

        self.chk_fax = QCheckBox("传真号")
        self.chk_fax.setChecked('传真号' in types)
        g1_layout.addWidget(self.chk_fax)

        self.chk_employee_id = QCheckBox("工号/学号")
        self.chk_employee_id.setChecked('工号/学号' in types)
        g1_layout.addWidget(self.chk_employee_id)

        self.chk_project_code = QCheckBox("项目代号")
        self.chk_project_code.setChecked('项目代号' in types)
        g1_layout.addWidget(self.chk_project_code)

        self.chk_postal = QCheckBox("邮编 (330000)")
        self.chk_postal.setChecked('邮编' in types)
        g1_layout.addWidget(self.chk_postal)

        # 党政公文专用
        gov_label = QLabel("党政公文专用:")
        gov_label.setStyleSheet("font-size: 12px; color: #8b92a5; margin-top: 8px;")
        g1_layout.addWidget(gov_label)

        self.chk_docnum = QCheckBox("公文份号 (№******)")
        self.chk_docnum.setChecked('公文份号' in types)
        g1_layout.addWidget(self.chk_docnum)

        self.chk_doclevel = QCheckBox("密级标注 (绝密★***年)")
        self.chk_doclevel.setChecked('公文密级' in types)
        g1_layout.addWidget(self.chk_doclevel)

        self.chk_docref = QCheckBox("公文文号 (〔2024〕*字第***号)")
        self.chk_docref.setChecked('公文文号' in types)
        g1_layout.addWidget(self.chk_docref)

        # 医疗档案专用
        med_label = QLabel("医疗档案专用:")
        med_label.setStyleSheet("font-size: 12px; color: #8b92a5; margin-top: 8px;")
        g1_layout.addWidget(med_label)

        self.chk_medicare = QCheckBox("医保卡号")
        self.chk_medicare.setChecked('医保号' in types)
        g1_layout.addWidget(self.chk_medicare)

        self.chk_medical_record = QCheckBox("病历号/门诊号")
        self.chk_medical_record.setChecked('病历号' in types)
        g1_layout.addWidget(self.chk_medical_record)

        layout.addWidget(group1)

        # 脱敏样式
        group2 = QGroupBox("脱敏样式")
        g2_layout = QVBoxLayout(group2)
        g2_layout.setSpacing(16)

        self.mask_edit = QLineEdit()
        self.mask_edit.setText(self.settings.get('mask_char', '*'))
        self.mask_edit.setMaxLength(1)
        self.mask_edit.setFixedWidth(60)
        g2_layout.addLayout(self.create_row("遮罩字符", self.mask_edit))

        self.chk_preserve = QCheckBox("保留首尾字符（如：138****5678）")
        self.chk_preserve.setChecked(self.settings.get('preserve_first_last', True))
        g2_layout.addWidget(self.chk_preserve)

        self.chk_pseudo_mode = QCheckBox("假名化模式（替换为真实格式的假数据）")
        self.chk_pseudo_mode.setChecked(self.settings.get('sanitize_mode') == 'pseudo')
        g2_layout.addWidget(self.chk_pseudo_mode)

        layout.addWidget(group2)

        # 自定义脱敏规则
        group3 = QGroupBox("自定义脱敏规则")
        g3_layout = QVBoxLayout(group3)
        g3_layout.setSpacing(16)

        custom_patterns = self.settings.get('custom_patterns', {'keywords': '', 'regex': ''})

        self.custom_keywords_edit = QLineEdit()
        self.custom_keywords_edit.setPlaceholderText("输入敏感词，用逗号分隔（如：公司名,项目名,人名）")
        self.custom_keywords_edit.setText(custom_patterns.get('keywords', ''))
        g3_layout.addLayout(self.create_row("自定义敏感词", self.custom_keywords_edit))

        self.custom_regex_edit = QLineEdit()
        self.custom_regex_edit.setPlaceholderText("输入正则表达式（如：\\d{4}-\\d{4}-\\d{4}）")
        self.custom_regex_edit.setText(custom_patterns.get('regex', ''))
        g3_layout.addLayout(self.create_row("自定义正则表达式", self.custom_regex_edit))

        layout.addWidget(group3)
        scroll.setWidget(widget)
        # 所有 checkbox 已创建，启用场景联动
        self._scene_ready = True
        return scroll

    # ===== 界面设置 =====
    def create_ui_tab(self):
        scroll = AutoFitScrollArea()

        scroll.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        widget.setMinimumWidth(800)  # 初始值，resizeEvent 会动态修正

        # 显示设置
        group1 = QGroupBox("显示")
        g1_layout = QVBoxLayout(group1)
        g1_layout.setSpacing(16)

        self.history_spin = QSpinBox()
        self.history_spin.setRange(10, 500)
        self.history_spin.setValue(self.settings.get('history_limit', 100))
        self.history_spin.setFixedWidth(80)
        g1_layout.addLayout(self.create_row("历史记录数量", self.history_spin))

        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 24)
        self.font_spin.setValue(self.settings.get('font_size', 14))
        self.font_spin.setFixedWidth(80)
        g1_layout.addLayout(self.create_row("字体大小", self.font_spin))

        self.row_spin = QSpinBox()
        self.row_spin.setRange(24, 48)
        self.row_spin.setValue(self.settings.get('table_row_height', 32))
        self.row_spin.setFixedWidth(80)
        g1_layout.addLayout(self.create_row("表格行高", self.row_spin))

        layout.addWidget(group1)

        # 交互设置
        group2 = QGroupBox("交互")
        g2_layout = QVBoxLayout(group2)
        g2_layout.setSpacing(12)

        self.chk_show_result = QCheckBox("处理完成后显示结果对话框")
        self.chk_show_result.setChecked(self.settings.get('show_result_dialog', True))
        g2_layout.addWidget(self.chk_show_result)

        self.chk_show_progress = QCheckBox("显示处理进度详情")
        self.chk_show_progress.setChecked(self.settings.get('show_progress_detail', True))
        g2_layout.addWidget(self.chk_show_progress)

        layout.addWidget(group2)
        scroll.setWidget(widget)
        return scroll

    # ===== 高级设置 =====
    def create_advanced_tab(self):
        scroll = AutoFitScrollArea()

        scroll.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        widget.setMinimumWidth(800)  # 初始值，resizeEvent 会动态修正

        # 日志设置
        group1 = QGroupBox("日志")
        g1_layout = QVBoxLayout(group1)
        g1_layout.setSpacing(16)

        self.log_combo = QComboBox()
        self.log_combo.addItems(['调试', '信息', '警告', '错误'])
        log_idx = {'debug': 0, 'info': 1, 'warn': 2, 'error': 3}
        self.log_combo.setCurrentIndex(log_idx.get(self.settings.get('log_level'), 1))
        self.log_combo.setMinimumWidth(120)
        g1_layout.addLayout(self.create_row("日志级别", self.log_combo))

        self.logsize_spin = QSpinBox()
        self.logsize_spin.setRange(1, 100)
        self.logsize_spin.setValue(self.settings.get('max_log_size_mb', 10))
        self.logsize_spin.setFixedWidth(80)
        g1_layout.addLayout(self.create_row("最大日志大小 (MB)", self.logsize_spin))

        layout.addWidget(group1)

        # 缓存设置
        group2 = QGroupBox("缓存")
        g2_layout = QVBoxLayout(group2)
        g2_layout.setSpacing(16)

        self.chk_cache = QCheckBox("启用缓存（加速重复处理）")
        self.chk_cache.setChecked(self.settings.get('cache_enabled', True))
        g2_layout.addWidget(self.chk_cache)

        self.cache_spin = QSpinBox()
        self.cache_spin.setRange(10, 1000)
        self.cache_spin.setValue(self.settings.get('cache_size_mb', 100))
        self.cache_spin.setFixedWidth(80)
        g2_layout.addLayout(self.create_row("缓存上限 (MB)", self.cache_spin))

        layout.addWidget(group2)

        # 数据管理
        group3 = QGroupBox("数据管理")
        g3_layout = QVBoxLayout(group3)
        g3_layout.setSpacing(12)

        self.btn_clear_history = QPushButton("清空所有历史记录")
        self.btn_clear_history.setProperty("secondary", True)
        self.btn_clear_history.clicked.connect(self.clear_history)
        g3_layout.addWidget(self.btn_clear_history)

        self.btn_clear_cache = QPushButton("清空缓存")
        self.btn_clear_cache.setProperty("secondary", True)
        self.btn_clear_cache.clicked.connect(self.clear_cache)
        g3_layout.addWidget(self.btn_clear_cache)

        layout.addWidget(group3)
        scroll.setWidget(widget)
        return scroll

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)

    def _apply_scene(self, scene: str):
        """场景预设：批量设置勾选状态（不保存，由用户手动点保存生效）"""
        # UI 未完全创建时跳过（防止初始化时信号触发）
        if not getattr(self, '_scene_ready', False):
            return
        # 防止 radio button 切换时级联触发
        if getattr(self, '_scene_applying', False):
            return
        self._scene_applying = True

        # 先全部取消，再按场景勾选
        all_chks = [
            self.chk_phone, self.chk_email, self.chk_idcard, self.chk_bankcard,
            self.chk_ip, self.chk_passport, self.chk_mac, self.chk_imei,
            self.chk_plate, self.chk_social, self.chk_credit, self.chk_contract,
            self.chk_amount, self.chk_license, self.chk_phone_biz,
            self.chk_docnum, self.chk_doclevel, self.chk_docref,
            self.chk_medicare, self.chk_medical_record,
            self.chk_account_permit, self.chk_purchase_order,
            self.chk_fax, self.chk_employee_id,
            self.chk_project_code, self.chk_postal,
        ]
        for c in all_chks:
            c.setChecked(False)

        if scene == 'general':
            for c in [self.chk_phone, self.chk_email, self.chk_idcard,
                      self.chk_bankcard, self.chk_ip, self.chk_passport,
                      self.chk_mac, self.chk_imei, self.chk_plate,
                      self.chk_credit, self.chk_contract, self.chk_amount,
                      self.chk_license, self.chk_phone_biz,
                      self.chk_account_permit, self.chk_purchase_order,
                      self.chk_fax, self.chk_employee_id,
                      self.chk_project_code, self.chk_postal]:
                c.setChecked(True)
        elif scene == 'gov':
            for c in [self.chk_phone, self.chk_email, self.chk_idcard,
                      self.chk_bankcard, self.chk_ip, self.chk_passport,
                      self.chk_plate, self.chk_credit, self.chk_contract,
                      self.chk_amount, self.chk_license,
                      self.chk_docnum, self.chk_doclevel, self.chk_docref,
                      self.chk_account_permit, self.chk_purchase_order,
                      self.chk_fax, self.chk_employee_id,
                      self.chk_project_code, self.chk_postal]:
                c.setChecked(True)
        elif scene == 'finance':
            for c in [self.chk_phone, self.chk_email, self.chk_idcard,
                      self.chk_bankcard, self.chk_ip, self.chk_passport,
                      self.chk_mac, self.chk_imei, self.chk_plate,
                      self.chk_social, self.chk_credit, self.chk_contract,
                      self.chk_amount, self.chk_phone_biz,
                      self.chk_account_permit, self.chk_purchase_order,
                      self.chk_fax, self.chk_employee_id,
                      self.chk_project_code, self.chk_postal]:
                c.setChecked(True)
        elif scene == 'medical':
            for c in [self.chk_phone, self.chk_email, self.chk_idcard,
                      self.chk_bankcard, self.chk_ip, self.chk_passport,
                      self.chk_medicare, self.chk_medical_record,
                      self.chk_social, self.chk_credit, self.chk_contract,
                      self.chk_amount, self.chk_license, self.chk_phone_biz,
                      self.chk_account_permit, self.chk_purchase_order,
                      self.chk_fax, self.chk_employee_id,
                      self.chk_project_code, self.chk_postal]:
                c.setChecked(True)
        elif scene == 'edu':
            for c in [self.chk_phone, self.chk_email, self.chk_idcard,
                      self.chk_bankcard, self.chk_ip, self.chk_passport,
                      self.chk_mac, self.chk_imei, self.chk_plate,
                      self.chk_credit, self.chk_contract, self.chk_amount,
                      self.chk_license, self.chk_phone_biz,
                      self.chk_account_permit, self.chk_purchase_order,
                      self.chk_fax, self.chk_employee_id,
                      self.chk_project_code, self.chk_postal]:
                c.setChecked(True)

        elif scene == 'custom':
            # 自定义场景：全部勾选
            all_checks = [
                self.chk_phone, self.chk_email, self.chk_idcard, self.chk_bankcard,
                self.chk_ip, self.chk_passport, self.chk_mac, self.chk_imei,
                self.chk_plate, self.chk_social, self.chk_credit, self.chk_contract,
                self.chk_amount, self.chk_license, self.chk_phone_biz,
                self.chk_docnum, self.chk_doclevel, self.chk_docref,
                self.chk_medicare, self.chk_medical_record,
                self.chk_account_permit, self.chk_purchase_order,
                self.chk_fax, self.chk_employee_id,
                self.chk_project_code, self.chk_postal,
            ]
            for c in all_checks:
                c.setChecked(True)

        self._scene_applying = False

        # 场景切换后同步到其他标签页
        self._propagate_sanitize_types()

    def get_sanitize_types(self):
        types = []
        if self.chk_phone.isChecked():
            types.append('手机号')
        if self.chk_email.isChecked():
            types.append('邮箱')
        if self.chk_idcard.isChecked():
            types.append('身份证')
        if self.chk_bankcard.isChecked():
            types.append('银行卡')
        if self.chk_ip.isChecked():
            types.append('IP地址')
        if self.chk_passport.isChecked():
            types.append('护照号')
        if self.chk_mac.isChecked():
            types.append('Mac地址')
        if self.chk_imei.isChecked():
            types.append('IMEI')
        if self.chk_plate.isChecked():
            types.append('车牌号')
        if self.chk_social.isChecked():
            types.append('社保卡号')
        if self.chk_credit.isChecked():
            types.append('社会信用代码')
        if self.chk_contract.isChecked():
            types.append('合同编号')
        if self.chk_amount.isChecked():
            types.append('投标/成交价')
        if self.chk_license.isChecked():
            types.append('营业执照号')
        if self.chk_phone_biz.isChecked():
            types.append('固定电话')
        if self.chk_docnum.isChecked():
            types.append('公文份号')
        if self.chk_doclevel.isChecked():
            types.append('公文密级')
        if self.chk_docref.isChecked():
            types.append('公文文号')
        if self.chk_medicare.isChecked():
            types.append('医保号')
        if self.chk_medical_record.isChecked():
            types.append('病历号')
        if self.chk_account_permit.isChecked():
            types.append('开户许可证号')
        if self.chk_purchase_order.isChecked():
            types.append('采购/订单编号')
        if self.chk_fax.isChecked():
            types.append('传真号')
        if self.chk_employee_id.isChecked():
            types.append('工号/学号')
        if self.chk_project_code.isChecked():
            types.append('项目代号')
        if self.chk_postal.isChecked():
            types.append('邮编')
        return types

    def on_language_changed(self, index):
        """语言下拉框选择后立即生效"""
        lang = 'zh-CN' if index == 0 else 'en-US'
        self.settings['language'] = lang
        self._propagate_language()

    def on_theme_changed(self, index):
        themes = ['light', 'dark', 'system']
        theme = themes[index]
        self.settings['theme'] = theme
        self.save_settings()
        if self.theme_callback:
            self.theme_callback(theme)

    def on_save(self):
        # 通用
        self.settings['language'] = 'zh-CN' if self.lang_combo.currentIndex() == 0 else 'en-US'
        self.settings['auto_check_update'] = self.chk_auto_update.isChecked()
        self.settings['minimize_to_tray'] = self.chk_minimize_tray.isChecked()
        self.settings['confirm_on_exit'] = self.chk_confirm_exit.isChecked()

        # 输出
        self.settings['output_dir'] = self.output_dir_edit.text()
        self.settings['auto_backup'] = self.chk_auto_backup.isChecked()
        self.settings['overwrite_confirm'] = self.chk_overwrite_confirm.isChecked()
        self.settings['preserve_structure'] = self.chk_preserve_structure.isChecked()
        self.settings['timestamp_output'] = self.chk_timestamp.isChecked()

        # 处理
        self.settings['workers'] = self.workers_spin.value()
        self.settings['image_quality'] = self.img_slider.value()
        self.settings['text_compression'] = self.text_slider.value()
        self.settings['pdf_quality'] = self.pdf_slider.value()
        self.settings['remove_empty_lines'] = self.chk_remove_empty.isChecked()
        self.settings['remove_empty_paragraphs'] = self.chk_remove_empty_para.isChecked()
        self.settings['deep_clean_word'] = self.chk_deep_clean.isChecked()
        self.settings['embed_images'] = self.chk_embed.isChecked()

        # 脱敏
        self.settings['sanitize_types'] = self.get_sanitize_types()
        self.settings['mask_char'] = self.mask_edit.text() or '*'
        self.settings['preserve_first_last'] = self.chk_preserve.isChecked()
        self.settings['sanitize_mode'] = 'pseudo' if self.chk_pseudo_mode.isChecked() else 'mask'
        self.settings['custom_patterns'] = {
            'keywords': self.custom_keywords_edit.text(),
            'regex': self.custom_regex_edit.text()
        }

        # 界面
        self.settings['history_limit'] = self.history_spin.value()
        self.settings['font_size'] = self.font_spin.value()
        self.settings['table_row_height'] = self.row_spin.value()
        self.settings['show_result_dialog'] = self.chk_show_result.isChecked()
        self.settings['show_progress_detail'] = self.chk_show_progress.isChecked()

        # 高级
        log_levels = ['debug', 'info', 'warn', 'error']
        self.settings['log_level'] = log_levels[self.log_combo.currentIndex()]
        self.settings['max_log_size_mb'] = self.logsize_spin.value()
        self.settings['cache_enabled'] = self.chk_cache.isChecked()
        self.settings['cache_size_mb'] = self.cache_spin.value()

        self.save_settings()

        # ===== 即时生效 =====
        self._apply_font_size()
        self._apply_table_row_height()
        self._propagate_sanitize_types()
        self._propagate_language()
        self.settings_changed.emit(self.settings)

        self.btn_save.setText("已保存 ✓")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.btn_save.setText("保存设置"))

    # ===== 即时生效方法 =====

    def _apply_font_size(self):
        """即时应用字体大小"""
        font_size = self.settings.get('font_size', 14)
        app = None
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            from PySide6.QtGui import QFont
            font = QFont("Microsoft YaHei", font_size)
            font.setStyleHint(QFont.StyleHint.SansSerif)
            app.setFont(font)

    def _apply_table_row_height(self):
        """即时应用表格行高"""
        row_height = self.settings.get('table_row_height', 32)
        # 通知主窗口下所有表格更新行高
        if self._main_window:
            from PySide6.QtWidgets import QTableWidget
            for tab in [self._main_window.tab_batch, self._main_window.tab_history]:
                if hasattr(tab, 'file_table') and isinstance(tab.file_table, QTableWidget):
                    tab.file_table.verticalHeader().setDefaultSectionSize(row_height)

    def _propagate_sanitize_types(self):
        """将脱敏类型同步到文档脱敏和批量处理标签页"""
        types = self.settings.get('sanitize_types', [])
        if not self._main_window:
            return

        # 同步到 sanitize_tab
        sanitize_tab = getattr(self._main_window, 'tab_sanitize', None)
        if sanitize_tab and hasattr(sanitize_tab, 'refresh_sanitize_types'):
            sanitize_tab.refresh_sanitize_types(types)

        # 同步到 batch_tab
        batch_tab = getattr(self._main_window, 'tab_batch', None)
        if batch_tab and hasattr(batch_tab, 'refresh_sanitize_types'):
            batch_tab.refresh_sanitize_types(types)

    def _propagate_language(self):
        """传播语言变更到主窗口"""
        if self._main_window and hasattr(self._main_window, 'apply_language'):
            lang = self.settings.get('language', 'zh-CN')
            self._main_window.apply_language(lang)

    def on_reset(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.save_settings()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "提示", "已恢复默认设置，重启软件后生效。")

    def clear_history(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有历史记录吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            history_file = Path(__file__).parent / 'processing_history.json'
            if history_file.exists():
                history_file.unlink()
            QMessageBox.information(self, "完成", "历史记录已清空。")

    def clear_cache(self):
        from PySide6.QtWidgets import QMessageBox
        cache_dir = Path(__file__).parent / 'cache'
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir, ignore_errors=True)
        QMessageBox.information(self, "完成", "缓存已清空。")

    def get_settings(self):
        return self.settings

    def update_language(self, lang):
        """更新语言"""
        from translations import get_translation
        _ = lambda t: get_translation(t, lang)

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

        # 更新按钮
        if hasattr(self, 'btn_save'):
            self.btn_save.setText(_('保存设置'))
        if hasattr(self, 'btn_reset'):
            self.btn_reset.setText(_('恢复默认'))
        if hasattr(self, 'btn_clear_history'):
            self.btn_clear_history.setText(_('清空所有历史记录'))
        if hasattr(self, 'btn_clear_cache'):
            self.btn_clear_cache.setText(_('清空缓存'))

        # 更新语言下拉框
        if hasattr(self, 'lang_combo'):
            self.lang_combo.setItemText(0, _('简体中文'))
            self.lang_combo.setItemText(1, 'English')
