# -*- coding: utf-8 -*-
"""
SafeShrink 主题管理器 v2.1
深色主题：侧边栏/内容区分层配色，确保每个区域的文字都清晰可读
"""

import os, sys
from PySide6.QtWidgets import QApplication, QTableView
cal_qtableview = QTableView  # 用于 findChildren 的类型引用
from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtCore import Qt


def _resource_path(relative_path):
    """
    获取资源文件的绝对路径，兼容 PyInstaller 打包和源码运行。
    
    Args:
        relative_path: 相对于项目根目录的路径（如 'assets/icon.png'）
    
    Returns:
        str: 资源文件的绝对路径
    
    PyInstaller onedir 模式：
        - EXE 在 dist/SafeShrink/
        - 资源在 dist/SafeShrink/_internal/
        - sys._MEIPASS 指向 _internal 目录
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller onedir: exe 所在目录的 _internal
        base = os.path.join(sys._MEIPASS)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path).replace('\\', '/')


_COMBO_ARROW = _resource_path('assets/arrow_down.png')
_SPIN_UP_ARROW = _resource_path('assets/arrow_up.png')
_SPIN_DOWN_ARROW = _resource_path('assets/arrow_down2.png')


class ThemeManager:

    # ============================================================
    # 深色主题 - 侧边栏深色 + 内容区深色（但比侧边栏浅）
    # 文字按区域独立配色，确保对比度
    # ============================================================
    DARK_THEME = {
        # ---------- 侧边栏（最深背景 #11111b）----------
        # 侧边栏文字要非常亮才能看清
        'sidebar_bg': '#11111b',
        'sidebar_hover': '#1e1e2e',
        'sidebar_active': '#89b4fa',
        'sidebar_text': '#e6edf3',       # 高亮白 - 主导航文字
        'sidebar_text_active': '#11111b',
        'sidebar_text_muted': '#8b949e',  # 暗淡灰 - 底部版本号

        # ---------- 内容区（深色背景 #1e1e2e）----------
        'window_bg': '#1e1e2e',
        'content_bg': '#1e1e2e',

        # 内容区卡片/输入框
        'card_bg': '#252536',
        'card_hover': '#2d2d42',
        'input_bg': '#252536',

        # 表格交替行
        'table_alt_bg': '#2a2a42',

        # ---------- 内容区文字 ----------
        # 深色背景上用淡蓝白色，有科技感且清晰
        'text_primary': '#c5d3e8',        # 主文字 - 高对比
        'text_secondary': '#9caaC8',     # 次要文字
        'text_muted': '#5c6a82',         # 弱化文字 - 在深背景上仍可见
        'text_link': '#89b4fa',          # 链接色

        # ---------- 边框 ----------
        'border': '#3d3d5c',
        'border_light': '#2a2a42',
        'divider': '#2d2d48',

        # ---------- 强调色 ----------
        'accent': '#89b4fa',
        'accent_hover': '#a6c8ff',
        'accent_pressed': '#74c7ec',
        'accent_light': 'rgba(137, 180, 250, 0.12)',
        'accent_text': '#89b4fa',

        # ---------- 状态色 ----------
        'success': '#a6e3a1',
        'success_bg': 'rgba(166, 227, 161, 0.12)',
        'success_text': '#a6e3a1',

        'warning': '#f9e2af',
        'warning_bg': 'rgba(249, 226, 175, 0.12)',
        'warning_text': '#f9e2af',

        'error': '#f38ba8',
        'error_bg': 'rgba(243, 139, 168, 0.12)',
        'error_text': '#f38ba8',

        'info': '#89b4fa',
        'info_bg': 'rgba(137, 180, 250, 0.12)',
        'info_text': '#89b4fa',

        # ---------- 交互状态 ----------
        'hover': '#2a2a42',
        'selected': '#353555',
        'pressed': '#3d3d60',

        # ---------- 阴影 ----------
        'shadow': 'rgba(0, 0, 0, 0.35)',
        'shadow_light': 'rgba(0, 0, 0, 0.18)',
    }

    # ============================================================
    # 浅色主题 - 侧边栏深色 + 内容区浅色
    # 文字按区域独立配色，确保对比度
    # ============================================================
    LIGHT_THEME = {
        # ---------- 侧边栏（深色背景）----------
        'sidebar_bg': '#1e1e2e',
        'sidebar_hover': '#2d2d42',
        'sidebar_active': '#89b4fa',
        'sidebar_text': '#e6edf3',        # 高亮白
        'sidebar_text_active': '#1e1e2e',
        'sidebar_text_muted': '#8b949e',  # 暗淡灰

        # ---------- 内容区（白色背景）----------
        'window_bg': '#ffffff',
        'content_bg': '#ffffff',

        'card_bg': '#f7f8fa',
        'card_hover': '#f0f1f4',
        'input_bg': '#ffffff',

        # 表格交替行
        'table_alt_bg': '#ffffff',

        # ---------- 内容区文字 - 深色系 ----------
        # 白色背景上用深色文字，标准做法
        'text_primary': '#1a1a2e',        # 主文字 - 深色高对比
        'text_secondary': '#4a5568',       # 次要文字
        'text_muted': '#9ca3af',          # 弱化文字
        'text_link': '#0066cc',           # 链接色 - 蓝色

        # ---------- 边框 ----------
        'border': '#e2e4ea',
        'border_light': '#f0f1f4',
        'divider': '#eaecef',

        # ---------- 强调色 ----------
        'accent': '#5b5fc7',
        'accent_hover': '#4a4eb5',
        'accent_pressed': '#3d3ea0',
        'accent_light': 'rgba(91, 95, 199, 0.08)',
        'accent_text': '#5b5fc7',

        # ---------- 状态色 ----------
        'success': '#2e7d32',
        'success_bg': '#e8f5e9',
        'success_text': '#2e7d32',

        'warning': '#ed6c02',
        'warning_bg': '#fff4e5',
        'warning_text': '#ed6c02',

        'error': '#d32f2f',
        'error_bg': '#ffebee',
        'error_text': '#d32f2f',

        'info': '#0288d1',
        'info_bg': '#e1f5fe',
        'info_text': '#0288d1',

        # ---------- 交互状态 ----------
        'hover': '#f3f4f8',
        'selected': '#e8eaf0',
        'pressed': '#dfe1e8',

        # ---------- 阴影 ----------
        'shadow': 'rgba(0, 0, 0, 0.08)',
        'shadow_light': 'rgba(0, 0, 0, 0.04)',
    }

    # ============================================================
    # 日历弹窗专用样式（关键：必须显式设置格子文字色，否则深色主题下不可见）
    # ============================================================
    CALENDAR_STYLE = """

    QCalendarWidget {{
        background-color: {c|window_bg|};
        border: 1px solid {c|border|};
        font-size: 13px;
    /* Navigation / day-name column width (critical for Chinese) */
    QCalendarWidget QAbstractButton {{
        min-width: 44px;
    }}
    /* Reset toolbutton so it inherits min-width */
    QCalendarWidget QToolButton {{
        min-width: 0;
    }}

    }}
    QCalendarWidget QToolButton {{
        background-color: {c|card_bg|};
        color: {c|text_primary|};
        border: 1px solid {c|border|};
        border-radius: 4px;
        padding: 4px 8px;
    }}
    QCalendarWidget QToolButton:hover {{
        background-color: '{c|accent_light|}';
    }}
    QCalendarWidget QSpinBox {{
        background-color: {c|card_bg|};
        color: {c|text_primary|};
        border: 1px solid {c|border|};
        border-radius: 4px;
        padding: 2px 4px;
    }}
    QCalendarWidget QMenu {{
        background-color: {c|window_bg|};
        color: {c|text_primary|};
        border: 1px solid {c|border|};
    }}
    QCalendarWidget QMenu::item:selected {{
        background-color: {c|accent|};
        color: {c|text_primary|};
    }}
    QCalendarWidget QAbstractItemView {{
        background-color: {c|window_bg|};
        color: {c|text_primary|};
        border: none;
        padding: 0px;
        outline: none;
    }}
    QCalendarWidget QTableView {{
        background-color: {c|window_bg|};
        color: {c|text_primary|};
        gridline-color: {c|border|};
        border: none;
    }}
    QCalendarWidget QTableView::item {{
        color: {c|text_primary|};
        background-color: {c|window_bg|};
        border: none;
        padding: 2px;
    }}
    QCalendarWidget QTableView::item:hover {{
        background-color: {c|card_hover|};
    }}
    QCalendarWidget QTableView::item:selected {{
        background-color: {c|accent|};
        color: {c|text_primary|};
    }}
    QCalendarWidget QTableView::item:disabled {{
        color: {c|text_muted|};
        background-color: {c|window_bg|};
    }}

    """

    @staticmethod
    def get_theme_style(theme='dark'):
        """获取主题样式表"""
        c = ThemeManager.DARK_THEME if theme == 'dark' else ThemeManager.LIGHT_THEME

        return f'''
            /* ================================================
               SafeShrink 主题样式表 v2.1
               ================================================ */

            /* ===== 全局样式 ===== */
            QWidget {{
                background-color: {c['window_bg']};
                color: {c['text_primary']};
                font-family: "Segoe UI", "Microsoft YaHei", -apple-system, sans-serif;
                font-size: 14px;
            }}

            /* ===== 主窗口 ===== */
            QMainWindow {{
                background-color: {c['window_bg']};
            }}

            /* ===== 侧边栏 ===== */
            QFrame#sidebar {{
                background-color: {c['sidebar_bg']};
                border: none;
            }}

            /* 侧边栏 Logo 文字 */
            QFrame#sidebar QLabel {{
                color: {c['sidebar_text']};
                background: transparent;
            }}

            QFrame#sidebar QLabel#logo {{
                color: {c['sidebar_text']};
                font-size: 16px;
                font-weight: 700;
            }}

            QFrame#sidebar QLabel#footer {{
                color: {c['sidebar_text_muted']};
                font-size: 11px;
                background: transparent;
            }}

            QFrame#divider {{
                background-color: {c['divider']};
                border: none;
                max-height: 1px;
            }}

            /* ===== 导航列表 ===== */
            QListWidget#navList {{
                background-color: transparent;
                border: none;
                outline: none;
            }}

            QListWidget#navList::item {{
                color: {c['sidebar_text']};
                padding: 10px 14px;
                margin: 2px 8px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }}

            QListWidget#navList::item:hover {{
                background-color: {c['sidebar_hover']};
            }}

            QListWidget#navList::item:selected {{
                background-color: {c['sidebar_active']};
                color: {c['sidebar_text_active']};
                font-weight: 600;
            }}

            /* ===== 内容区域 ===== */
            QFrame#contentArea {{
                background-color: {c['content_bg']};
            }}

            QFrame#header {{
                background-color: transparent;
                border-bottom: 1px solid {c['divider']};
            }}

            /* 页面标题 */
            QLabel#pageTitle {{
                color: {c['text_primary']};
                font-size: 22px;
                font-weight: 700;
                letter-spacing: -0.3px;
                background: transparent;
            }}

            QLabel#pageSubtitle {{
                color: {c['text_muted']};
                font-size: 13px;
                margin-top: 2px;
                background: transparent;
            }}

            /* ===== 卡片 ===== */
            QFrame#card {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border_light']};
                border-radius: 12px;
            }}

            QFrame#cardFlat {{
                background-color: {c['card_bg']};
                border: none;
                border-radius: 12px;
            }}

            /* ===== 按钮 ===== */
            QPushButton {{
                background-color: {c['accent']};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
                min-height: 20px;
            }}

            QPushButton:hover {{
                background-color: {c['accent_hover']};
            }}

            QPushButton:pressed {{
                background-color: {c['accent_pressed']};
            }}

            QPushButton:disabled {{
                background-color: {c['border']};
                color: {c['text_muted']};
            }}

            /* 次要按钮 */
            QPushButton[class="secondary"] {{
                background-color: transparent;
                color: {c['text_primary']};
                border: 1px solid {c['border']};
            }}

            QPushButton[class="secondary"]:hover {{
                background-color: {c['hover']};
                border-color: {c['text_muted']};
            }}

            /* 图标按钮 */
            QPushButton[class="icon"] {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 8px;
                min-width: 36px;
                min-height: 36px;
            }}

            QPushButton[class="icon"]:hover {{
                background-color: {c['hover']};
            }}

            /* ===== 输入框 ===== */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {c['input_bg']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 10px 14px;
                color: {c['text_primary']};
                font-size: 14px;
                selection-background-color: {c['accent_light']};
            }}

            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {c['accent']};
            }}

            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
                background-color: {c['card_bg']};
                color: {c['text_muted']};
            }}

            QLineEdit::placeholder, QTextEdit::placeholder {{
                color: {c['text_muted']};
            }}

            /* ===== 下拉框 ===== */
            QComboBox {{
                background-color: {c['input_bg']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 8px 14px;
                color: {c['text_primary']};
                font-size: 14px;
                min-width: 100px;
            }}

            QComboBox:hover {{
                border-color: {c['text_muted']};
            }}

            QComboBox:focus {{
                border-color: {c['accent']};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 28px;
            }}

            QComboBox::down-arrow {{
                image: url({_COMBO_ARROW});
                width: 12px;
                height: 12px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 4px;
                selection-background-color: {c['accent_light']};
                outline: none;
                color: {c['text_primary']};
            }}

            /* ===== 标签页 ===== */
            QTabWidget {{
                border: none;
                background-color: {c['content_bg']};
            }}

            QTabWidget::pane {{
                border: none;
                background-color: {c['content_bg']};
            }}

            QTabBar {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {c['border_light']};
            }}

            QTabBar::tab {{
                background-color: transparent;
                color: {c['text_muted']};
                border: none;
                padding: 10px 18px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 14px;
                margin-right: 4px;
            }}

            QTabBar::tab:selected {{
                background-color: {c['accent_light']};
                color: {c['accent']};
                font-weight: 600;
            }}

            QTabBar::tab:hover:!selected {{
                background-color: {c['hover']};
                color: {c['text_primary']};
            }}

            /* ===== 表格 ===== */
            QTableWidget, QTableView {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border_light']};
                border-radius: 12px;
                gridline-color: {c['border_light']};
                outline: none;
                color: {c['text_primary']};
            }}

            QTableWidget::item, QTableView::item {{
                padding: 10px 14px;
                border-bottom: 1px solid {c['border_light']};
                color: {c['text_primary']};
            }}

            QTableWidget::item:hover, QTableView::item:hover {{
                background-color: {c['card_hover']};
            }}

            QTableWidget::item:alternate, QTableView::item:alternate {{
                background-color: {c['table_alt_bg']};
            }}

            QHeaderView::section {{
                background-color: {c['window_bg']};
                color: {c['text_secondary']};
                border: none;
                border-bottom: 2px solid {c['border']};
                padding: 10px 14px;
                font-weight: 600;
                font-size: 12px;
            }}

            /* ===== 滚动条 ===== */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                margin: 6px 2px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {c['border']};
                border-radius: 4px;
                min-height: 40px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {c['text_muted']};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}

            QScrollBar:horizontal {{
                background-color: transparent;
                height: 8px;
                margin: 2px 6px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {c['border']};
                border-radius: 4px;
                min-width: 40px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {c['text_muted']};
            }}

            /* ===== 分组框 ===== */
            QGroupBox {{
                font-weight: 600;
                font-size: 14px;
                color: {c['text_primary']};
                border: none;
                border-bottom: 1px solid {c['border_light']};
                border-left: 1px solid {c['border_light']};
                border-right: 1px solid {c['border_light']};
                border-radius: 12px;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                margin-top: 16px;
                padding: 16px 16px 12px 16px;
                background-color: transparent;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 14px;
                top: -6px;
                padding: 4px 12px 4px 12px;
                /* 跟随主题配色 */
                background-color: {c['card_bg']};
                color: {c['text_primary']};
                border-radius: 6px;
            }}

            /* ===== 复选框 ===== */
            QCheckBox {{
                spacing: 10px;
                color: {c['text_primary']};
                font-size: 14px;
            }}

            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {c['border']};
                border-radius: 6px;
                background-color: transparent;
            }}

            QCheckBox::indicator:hover {{
                border-color: {c['accent']};
            }}

            QCheckBox::indicator:checked {{
                background-color: {c['accent']};
                border-color: {c['accent']};
                image: none;
            }}

            QCheckBox::indicator:checked:hover {{
                background-color: {c['accent_hover']};
            }}

            QCheckBox::indicator:disabled {{
                background-color: {c['border']};
                border-color: {c['border']};
            }}

            /* ===== 进度条 ===== */
            QProgressBar {{
                background-color: {c['border']};
                border: none;
                border-radius: 6px;
                text-align: center;
                color: {c['text_primary']};
                font-weight: 600;
                font-size: 12px;
                min-height: 12px;
            }}

            QProgressBar::chunk {{
                background-color: {c['accent']};
                border-radius: 6px;
            }}

            /* ===== 滚动区域 ===== */
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}

            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}

            /* ===== 列表 ===== */
            QListWidget {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border_light']};
                border-radius: 12px;
                outline: none;
                color: {c['text_primary']};
            }}

            QListWidget::item {{
                padding: 10px 14px;
                border-radius: 8px;
                margin: 2px 4px;
                color: {c['text_primary']};
            }}

            QListWidget::item:selected {{
                background-color: {c['accent_light']};
                color: {c['accent']};
            }}

            QListWidget::item:hover:!selected {{
                background-color: {c['card_hover']};
            }}

            /* ===== 工具提示 ===== */
            QToolTip {{
                background-color: {c['card_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }}

            /* ===== 菜单 ===== */
            QMenu {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 12px;
                padding: 6px;
                color: {c['text_primary']};
            }}

            QMenu::item {{
                padding: 10px 20px;
                border-radius: 6px;
                color: {c['text_primary']};
            }}

            QMenu::item:selected {{
                background-color: {c['accent_light']};
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {c['border_light']};
                margin: 4px 8px;
            }}

            /* ===== 滑块 ===== */
            QSlider {{
                background-color: transparent;
                min-height: 24px;
            }}

            QSlider::groove:horizontal {{
                height: 6px;
                background-color: {c['border']};
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                width: 18px;
                height: 18px;
                background-color: {c['accent']};
                border-radius: 9px;
                border: 2px solid white;
                margin: -7px 0;
            }}

            QSlider::handle:horizontal:hover {{
                background-color: {c['accent_hover']};
            }}

            QSlider::sub-page:horizontal {{
                background-color: {c['accent']};
                border-radius: 3px;
            }}

            /* ===== 数值框 ===== */
            QSpinBox {{
                background-color: {c['input_bg']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 6px 10px;
                color: {c['text_primary']};
                font-size: 14px;
            }}

            QSpinBox:focus {{
                border-color: {c['accent']};
            }}

            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 20px;
                subcontrol-origin: border;
            }}

            QSpinBox::up-button {{
                subcontrol-position: top right;
            }}

            QSpinBox::down-button {{
                subcontrol-position: bottom right;
            }}

            QSpinBox::up-arrow {{
                image: url({_SPIN_UP_ARROW});
                width: 16px;
                height: 8px;
            }}

            QSpinBox::down-arrow {{
                image: url({_SPIN_DOWN_ARROW});
                width: 16px;
                height: 8px;
            }}

            /* ===== 拖拽提示 ===== */
            QLabel#dragHint {{
                background-color: {c['accent']};
                color: #ffffff;
                font-size: 15px;
                font-weight: 600;
                padding: 14px 28px;
                border-radius: 12px;
                border: 2px dashed rgba(255,255,255,0.5);
            }}

            /* ===== 状态标签 ===== */
            QLabel[class="status-success"] {{
                color: {c['success']};
                background-color: {c['success_bg']};
                padding: 4px 10px;
                border-radius: 6px;
            }}

            QLabel[class="status-warning"] {{
                color: {c['warning']};
                background-color: {c['warning_bg']};
                padding: 4px 10px;
                border-radius: 6px;
            }}

            QLabel[class="status-error"] {{
                color: {c['error']};
                background-color: {c['error_bg']};
                padding: 4px 10px;
                border-radius: 6px;
            }}

            /* ===== 提示文字 ===== */
            QLabel[class="hint-text"] {{
                color: {c['text_muted']};
                font-size: 12px;
            }}

            /* ===== 日历弹窗 ===== */
            QCalendarWidget {{
                background-color: {c['window_bg']};
                border: 1px solid {c['border']};
            }}

            QCalendarWidget QToolButton {{
                background-color: {c['card_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: '{c['accent_light']}';
            }}
            QCalendarWidget QSpinBox {{
                background-color: {c['card_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 2px 4px;
            }}
            QCalendarWidget QMenu {{
                background-color: {c['window_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
            }}
            QCalendarWidget QMenu::item:selected {{
                background-color: {c['accent']};
                color: {c['text_primary']};
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: {c['window_bg']};
                color: {c['text_primary']};
                border: none;
                padding: 0px;
                outline: none;
            }}
            QCalendarWidget QTableView {{
                background-color: {c['window_bg']};
                color: {c['text_primary']};
                gridline-color: {c['border']};
                border: none;
            }}
            QCalendarWidget QTableView::item {{
                color: {c['text_primary']};
                background-color: {c['window_bg']};
                border: none;
                padding: 2px;
            }}
            QCalendarWidget QTableView::item:hover {{
                background-color: {c['card_hover']};
            }}
            QCalendarWidget QTableView::item:selected {{
                background-color: {c['accent']};
                color: {c['text_primary']};
            }}
            QCalendarWidget QTableView::item:disabled {{
                color: {c['text_muted']};
                background-color: {c['window_bg']};
            }}
        '''

    @staticmethod
    def apply_theme(app, theme='dark'):
        """应用主题到 QApplication"""
        from theme_manager import ThemeManager
        theme_style = ThemeManager.get_theme_style(theme)
        app.setStyleSheet(theme_style)

    @staticmethod
    def apply_calendar_style(calendar_widget, theme='dark'):
        """
        将主题配色应用到日历弹窗（QCalendarWidget 实例）。
        必须在 QDateEdit.setCalendarPopup(True) 之后调用。
        """
        if calendar_widget is None:
            return
        c = ThemeManager.DARK_THEME if theme == 'dark' else ThemeManager.LIGHT_THEME
        # 三步替换：1) CSS {{ → {  2) {c|key|} 占位符格式  3) 值直接替换（无 .format() 无 tuple 问题）
        css = ThemeManager.CALENDAR_STYLE
        css = css.replace("{{", "{").replace("}}", "}")
        for k, v in c.items():
            css = css.replace("{c|" + k + "|}", v)

        # ── 2. 直接用 QPalette 设置表格背景，不依赖 CSS 继承 ─────
        # viewport 默认白色会覆盖 CSS background-color，必须强制覆盖
        from PySide6.QtGui import QPalette, QColor
        for tv in calendar_widget.findChildren(cal_qtableview):
            # 强制 viewport 背景 = 日历背景（关键修复）
            vp = tv.viewport()
            if vp:
                pal = vp.palette()
                pal.setColor(QPalette.ColorRole.Window, QColor(c['window_bg']))
                vp.setPalette(pal)
                vp.setBackgroundRole(QPalette.ColorRole.Window)
                vp.update()

        calendar_widget.setStyleSheet(css)

        # ── 3. 再次强制 QTableView 背景（确保 CSS 覆盖不住时也有保底）──
        for tv in calendar_widget.findChildren(cal_qtableview):
            pal = tv.palette()
            pal.setColor(QPalette.ColorRole.Base,      QColor(c['window_bg']))
            pal.setColor(QPalette.ColorRole.AlternateBase, QColor(c['table_alt_bg']))
            pal.setColor(QPalette.ColorRole.Window,   QColor(c['window_bg']))
            pal.setColor(QPalette.ColorRole.WindowText, QColor(c['text_primary']))
            tv.setPalette(pal)
            vp = tv.viewport()
            if vp:
                vp.update()


    @staticmethod
    def is_system_dark():
        """检测系统是否为暗色模式"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except:
            return False

    @staticmethod
    def get_actual_theme(setting):
        """获取实际主题"""
        if setting == 'system':
            return 'dark' if ThemeManager.is_system_dark() else 'light'
        return setting
