"""

SafeShrink Desktop - 主窗口 (带左侧栏现代布局)

"""



import sys

import os

from pathlib import Path



# 确保在 EXE 和直接运行都能找到同目录模块

_SCRIPT_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

if str(_SCRIPT_DIR) not in sys.path:

    sys.path.insert(0, str(_SCRIPT_DIR))



# 动态加载本地模块（onedir 模式）

# 用 SourceFileLoader 从源文件加载，绕过 PyInstaller PYZ

if getattr(sys, 'frozen', False):

    import importlib.machinery, importlib.util

    _src = _SCRIPT_DIR

    _fallback = _SCRIPT_DIR / '_internal'

    if not (_src / 'settings_tab.py').exists():

        if (_fallback / 'settings_tab.py').exists():

            _src = _fallback

        else:

            _src = _SCRIPT_DIR.parent

    for _n, _f in [

        ('slim_tab',        _src / 'slim_tab.py'),

        ('sanitize_tab',   _src / 'sanitize_tab.py'),

        ('batch_tab',      _src / 'batch_tab.py'),

        ('history_tab',    _src / 'history_tab.py'),

        ('history_manager',_src / 'history_manager.py'),

        ('settings_tab',   _src / 'settings_tab.py'),

        ('theme_manager',  _src / 'theme_manager.py'),

        ('safe_shrink',   _src / 'safe_shrink.py'),

        ('safe_shrink_gui',_src / 'safe_shrink_gui.py'),

        ('batch_processor',_src / 'batch_processor.py'),

        ('file_status',   _src / 'file_status.py'),

    ]:

        if _f.exists() and _n not in sys.modules:

            try:

                loader = importlib.machinery.SourceFileLoader(_n, str(_f))

                spec = importlib.util.spec_from_loader(_n, loader)

                if spec and spec.loader:

                    m = importlib.util.module_from_spec(spec)

                    sys.modules[_n] = m

                    spec.loader.exec_module(m)

            except Exception as e:

                pass

os.chdir(_SCRIPT_DIR)



# 高 DPI 支持



def _get_icon_path(theme='light'):

    """获取图标资源路径（支持 EXE 和源码运行）

    onedir 模式：exe 在 dist/main_window_v2/，资源在 dist/main_window_v2/_internal/assets/

    theme: 'light' 或 'dark'，决定使用哪个图标

    """

    if getattr(sys, 'frozen', False):

        base = Path(sys.executable).parent  # dist/main_window_v2/

        _internal = base / '_internal'

        if _internal.exists():

            base = _internal               # dist/main_window_v2/_internal/

    else:

        base = Path(__file__).parent        # 源码目录

    

    # 窗口/任务栏图标始终使用浅色06号素描图标

    return base / 'assets' / 'icon06_light.ico'



from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
# Qt 6.x enables high DPI support automatically
from PySide6.QtWidgets import (

    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,

    QLabel, QFrame, QSystemTrayIcon, QMenu, QStackedWidget,

    QListWidget, QListWidgetItem, QMessageBox, QPushButton,

    QStyle

)

from PySide6.QtCore import Qt, Signal, QTimer, QSize

from PySide6.QtGui import QFont, QAction



from slim_tab import SlimTab

from sanitize_tab import SanitizeTab

from batch_tab import BatchTab

from history_tab import HistoryTab

from history_manager import HistoryManager

from settings_tab import SettingsTab

from theme_manager import ThemeManager



# CLI 入口（延迟导入，CLI 模式不需要 PyQt6）

from safe_shrink import main as safe_shrink_main





class MainWindow(QMainWindow):

    files_dropped = Signal(list, str)



    NAV_ITEMS = [

        ("📄", "文件减肥", "slim"),

        ("🔒", "文档脱敏", "sanitize"),

        ("📁", "批量处理", "batch"),

        ("📋", "处理历史", "history"),

        ("⚙️", "设置", "settings"),

    ]



    @staticmethod

    def _get_base_dir():

        if getattr(sys, 'frozen', False):

            return Path.home() / 'AppData' / 'Roaming' / 'SafeShrink'

        return Path(__file__).parent



    def __init__(self):

        super().__init__()

        self.setWindowTitle("SafeShrink - 文档工具箱")

        self.setMinimumSize(1200, 750)

        self.resize(1200, 750)

        self.setAcceptDrops(True)



        # 设置窗口图标（任务栏、标题栏）

        try:

            icon_path = _get_icon_path()

            if icon_path.exists():

                from PySide6.QtGui import QIcon

                self.setWindowIcon(QIcon(str(icon_path)))

        except Exception as e:

            print(f"[SafeShrink] Icon load error: {e}")



        self.history_manager = HistoryManager()

        self.load_and_apply_theme()

        self.center()

        self.setup_ui()



        self.restore_timer = QTimer()

        self.restore_timer.setSingleShot(True)

        self.restore_timer.timeout.connect(self.restore_nav_style)

        self.hovered_nav = -1



        self.tray_icon = None

        self.setup_tray()

        self._is_dragging = False

        self.drag_hint = None



        # 延迟检查更新，避免启动时阻塞

        QTimer.singleShot(2000, self._delayed_update_check)



    def center(self):

        from PySide6.QtCore import QPoint

        screen = self.screen()

        if screen:

            geo = screen.geometry()

            self.move(

                QPoint(

                    (geo.width() - self.width()) // 2,

                    (geo.height() - self.height()) // 2

                )

            )



    def load_and_apply_theme(self):

        import json

        try:

            base_dir = self._get_base_dir()

            settings_file = base_dir / 'settings.json'

            theme = 'light'

            if settings_file.exists():

                with open(settings_file, 'r', encoding='utf-8') as f:

                    settings = json.load(f)

                theme = settings.get('theme', 'light')

            actual_theme = ThemeManager.get_actual_theme(theme)

            self.current_theme = theme

            self.setStyleSheet(ThemeManager.get_theme_style(actual_theme))

            self.update_theme_button()

        except Exception as e:

            print(f"[SafeShrink] Theme load error: {e}")

            self.current_theme = 'dark'

            self.setStyleSheet(ThemeManager.get_theme_style('dark'))



    def apply_theme(self, theme):

        try:

            actual_theme = ThemeManager.get_actual_theme(theme)

            self.current_theme = theme

            self.setStyleSheet(ThemeManager.get_theme_style(actual_theme))

            self.update_theme_button()

            self.update_window_icon()

            self.update_sidebar_logo()

            self.save_theme_setting(theme)

        except Exception as e:

            print(f"[SafeShrink] Apply theme error: {e}")



    def toggle_theme(self):

        """切换深色/浅色主题"""

        new_theme = 'light' if self.current_theme == 'dark' else 'dark'

        self.apply_theme(new_theme)



    def update_theme_button(self):

        """更新主题切换按钮文本"""

        if hasattr(self, 'theme_btn'):

            if self.current_theme == 'dark':

                self.theme_btn.setText("  🌙  深色模式")

            else:

                self.theme_btn.setText("  ☀️  浅色模式")



    def update_window_icon(self):

        """根据当前主题更新窗口图标（任务栏、标题栏）"""

        try:

            from PySide6.QtGui import QIcon

            actual_theme = ThemeManager.get_actual_theme(self.current_theme)

            icon_path = _get_icon_path(actual_theme)

            if icon_path.exists():

                self.setWindowIcon(QIcon(str(icon_path)))

        except Exception as e:

            print(f"[SafeShrink] Update icon error: {e}")



    def update_sidebar_logo(self):

        """根据当前主题更新侧边栏 Logo 图标"""

        if not hasattr(self, 'logo_icon'):

            return

        try:

            from PySide6.QtGui import QPixmap

            actual_theme = ThemeManager.get_actual_theme(self.current_theme)

            if actual_theme == 'dark':

                icon_path = _get_icon_path('dark').with_name('icon14_64x64_dark.png')

            else:

                icon_path = _get_icon_path('light').with_name('icon06_64x64_light.png')

            if icon_path.exists():

                pixmap = QPixmap(str(icon_path))

                scaled = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,

                                        Qt.TransformationMode.SmoothTransformation)

                self.logo_icon.setPixmap(scaled)

        except Exception as e:

            print(f"[SafeShrink] Update sidebar logo error: {e}")



    def save_theme_setting(self, theme):

        """保存主题设置"""

        import json

        try:

            base_dir = self._get_base_dir()

            settings_file = base_dir / 'settings.json'

            settings = {}

            if settings_file.exists():

                with open(settings_file, 'r', encoding='utf-8') as f:

                    settings = json.load(f)

            settings['theme'] = theme

            with open(settings_file, 'w', encoding='utf-8') as f:

                json.dump(settings, f, indent=2)

        except Exception as e:

            print(f"[SafeShrink] Save theme error: {e}")

        except Exception as e:

            print(f"[SafeShrink] Apply theme error: {e}")



    def setup_ui(self):

        # 必须在 create_sidebar 之前创建 stack（避免 currentRowChanged 信号触发时 stack 未定义）

        self.stack = QStackedWidget()

        self.stack.setObjectName("contentStack")



        central = QWidget()

        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.setSpacing(0)



        self.sidebar = self.create_sidebar()

        main_layout.addWidget(self.sidebar)



        self.content_area = self.create_content_area()

        main_layout.addWidget(self.content_area, 1)



    def create_sidebar(self):

        sidebar = QFrame()

        sidebar.setObjectName("sidebar")

        sidebar.setFixedWidth(220)



        layout = QVBoxLayout(sidebar)

        layout.setContentsMargins(12, 28, 12, 16)  # 顶部28px，确保logo不被任务栏遮挡

        layout.setSpacing(4)



        # Logo 区域

        logo_frame = QFrame()

        logo_frame.setObjectName("cardFlat")

        logo_frame.setStyleSheet("""

            QFrame#cardFlat {

                background-color: rgba(137, 180, 250, 0.08);

                border-radius: 14px;

                padding: 6px;

                margin-bottom: 8px;

            }

        """)

        logo_layout = QHBoxLayout(logo_frame)

        logo_layout.setContentsMargins(14, 14, 14, 10)  # 顶部14px（避开任务栏），底部10px

        logo_layout.setSpacing(12)



        # Logo 图标（根据主题选择：深色用14号漩涡，浅色用06号素描）

        self.logo_icon = QLabel()

        self.logo_icon.setStyleSheet("background: transparent;")

        try:

            from PySide6.QtGui import QPixmap

            # 获取当前实际主题

            actual_theme = ThemeManager.get_actual_theme(self.current_theme)

            # 根据主题选择图标文件

            if actual_theme == 'dark':

                icon_path = _get_icon_path('dark').with_name('icon14_64x64_dark.png')

            else:

                icon_path = _get_icon_path('light').with_name('icon06_64x64_light.png')

            if icon_path.exists():

                pixmap = QPixmap(str(icon_path))

                scaled = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,

                                        Qt.TransformationMode.SmoothTransformation)

                self.logo_icon.setPixmap(scaled)

                self.logo_icon.setFixedSize(64, 64)

            else:

                self.logo_icon.setText("📎")

                self.logo_icon.setFont(QFont("Segoe UI", 24))

        except Exception:

            self.logo_icon.setText("📎")

            self.logo_icon.setFont(QFont("Segoe UI", 24))



        # Logo 文字

        logo_text = QVBoxLayout()

        logo_text.setSpacing(2)

        logo_label = QLabel("SafeShrink")

        logo_label.setObjectName("logo")

        logo_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))

        logo_label.setStyleSheet("background: transparent;")



        logo_sub = QLabel("密小件")

        logo_sub.setFont(QFont("Segoe UI", 11))

        logo_sub.setStyleSheet("background: transparent; color: #8b949e;")

        logo_text.addWidget(logo_label)

        logo_text.addWidget(logo_sub)



        logo_layout.addWidget(self.logo_icon)

        logo_layout.addLayout(logo_text)

        logo_layout.addStretch()

        layout.addWidget(logo_frame)



        # 分隔线

        divider = QFrame()

        divider.setFrameShape(QFrame.Shape.HLine)

        divider.setObjectName("divider")

        divider.setFixedHeight(1)

        divider.setStyleSheet("background-color: #313244;")

        layout.addWidget(divider)

        layout.addSpacing(12)



        # 导航列表

        self.nav_list = QListWidget()

        self.nav_list.setObjectName("navList")

        self.nav_list.setFrameShape(QFrame.Shape.NoFrame)

        self.nav_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.nav_list.setIconSize(QSize(22, 22))

        self.nav_list.setSpacing(4)



        for icon, text, key in self.NAV_ITEMS:

            item = QListWidgetItem(f"  {icon}  {text}")

            item.setData(Qt.ItemDataRole.UserRole, key)

            item.setToolTip(text)

            self.nav_list.addItem(item)



        self.nav_list.currentRowChanged.connect(self.on_nav_changed)

        self.nav_list.setCurrentRow(0)

        layout.addWidget(self.nav_list, 1)



        # 底部区域 - 主题切换

        bottom_frame = QFrame()

        bottom_frame.setStyleSheet("background: transparent;")

        bottom_layout = QVBoxLayout(bottom_frame)

        bottom_layout.setContentsMargins(0, 0, 0, 0)

        bottom_layout.setSpacing(8)



        # 主题切换按钮

        self.theme_btn = QPushButton()

        self.theme_btn.setObjectName("themeToggle")

        self.theme_btn.setText("  🌙  深色模式")

        self.theme_btn.setFont(QFont("Segoe UI", 12))

        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.theme_btn.setStyleSheet("""

            QPushButton {

                background-color: transparent;

                color: #bac2de;

                border: 1px solid #45475a;

                border-radius: 8px;

                padding: 10px 12px;

                text-align: left;

            }

            QPushButton:hover {

                background-color: #1e1e2e;

            }

        """)

        self.theme_btn.clicked.connect(self.toggle_theme)

        bottom_layout.addWidget(self.theme_btn)



        # 版本信息

        footer = QLabel("v0.9.0  SafeShrink")

        footer.setObjectName("footer")

        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        footer.setFont(QFont("Segoe UI", 10))

        footer.setStyleSheet("background: transparent;")

        bottom_layout.addWidget(footer)



        layout.addWidget(bottom_frame)



        return sidebar



    def create_content_area(self):

        content = QFrame()

        content.setObjectName("contentArea")

        content.setFrameShape(QFrame.Shape.NoFrame)  # 清除所有边框，防止白线

        content.setFrameShadow(QFrame.Shadow.Plain)

        content.setLineWidth(0)

        layout = QVBoxLayout(content)

        layout.setContentsMargins(24, 20, 24, 24)

        layout.setSpacing(0)



        # 标题栏

        header = QFrame()

        header.setObjectName("header")

        header_layout = QVBoxLayout(header)

        header_layout.setContentsMargins(0, 0, 0, 16)



        self.page_title = QLabel("文件减肥")

        self.page_title.setObjectName("pageTitle")

        self.page_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))



        self.page_subtitle = QLabel("智能压缩文档，减小文件体积")

        self.page_subtitle.setObjectName("pageSubtitle")



        header_layout.addWidget(self.page_title)

        header_layout.addWidget(self.page_subtitle)

        layout.addWidget(header)



        # 内容堆叠（已在 setup_ui 提前创建）

        self.tab_slim = SlimTab()

        self.tab_sanitize = SanitizeTab()

        self.tab_batch = BatchTab()

        self.tab_history = HistoryTab(self.history_manager)

        self.tab_settings = SettingsTab()

        self.tab_settings.set_theme_callback(self.apply_theme)
        self.tab_settings._main_window = self  # 注入主窗口引用
        self.tab_settings.settings_changed.connect(self.on_settings_changed)



        self.stack.addWidget(self.tab_slim)

        self.stack.addWidget(self.tab_sanitize)

        self.stack.addWidget(self.tab_batch)

        self.stack.addWidget(self.tab_history)

        self.stack.addWidget(self.tab_settings)



        layout.addWidget(self.stack)



        # 拖拽提示

        self.drag_hint = QLabel("📂 松开鼠标添加文件", self)

        self.drag_hint.setObjectName("dragHint")

        self.drag_hint.setStyleSheet("""

            QLabel#dragHint {

                background-color: rgba(76, 175, 80, 0.95);

                color: white;

                font-size: 18px;

                font-weight: bold;

                padding: 20px 40px;

                border-radius: 12px;

                border: 2px dashed white;

            }

        """)

        self.drag_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.drag_hint.hide()



        return content



    def on_nav_changed(self, index):

        # 防御性检查：信号可能在 setup_ui 完成前就被触发

        if not all(hasattr(self, attr) for attr in ['stack', 'page_title', 'page_subtitle']):

            return

        if 0 <= index < len(self.NAV_ITEMS):

            self.stack.setCurrentIndex(index)

            icon, text, key = self.NAV_ITEMS[index]

            self.page_title.setText(text)

            subtitles = {

                "slim": "📄 智能压缩文档，减小文件体积",

                "sanitize": "🔒 自动识别并脱敏敏感信息",

                "batch": "📁 批量处理多个文件",

                "history": "📋 查看和管理处理记录",

                "settings": "⚙️ 配置应用偏好",

            }

            self.page_subtitle.setText(subtitles.get(key, ""))



    def on_settings_changed(self, settings):
        """设置变更回调：通知相关标签页刷新"""
        try:
            # 脱敏类型同步
            types = settings.get('sanitize_types', [])
            if hasattr(self, 'tab_sanitize') and hasattr(self.tab_sanitize, 'refresh_sanitize_types'):
                self.tab_sanitize.refresh_sanitize_types(types)
            if hasattr(self, 'tab_batch') and hasattr(self.tab_batch, 'refresh_sanitize_types'):
                self.tab_batch.refresh_sanitize_types(types)
            
            # 处理参数同步（线程数、图片质量、文本压缩）
            if hasattr(self, 'tab_batch') and hasattr(self.tab_batch, 'refresh_from_settings'):
                self.tab_batch.refresh_from_settings(settings)
            
            # 界面设置同步
            font_size = settings.get('font_size', 14)
            row_height = settings.get('table_row_height', 32)
            from PySide6.QtGui import QFont
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                font = QFont('Microsoft YaHei', font_size)
                font.setStyleHint(QFont.StyleHint.SansSerif)
                app.setFont(font)
            from PySide6.QtWidgets import QTableWidget
            for tab in [getattr(self, 'tab_batch', None), getattr(self, 'tab_history', None)]:
                if tab and hasattr(tab, 'file_table') and isinstance(tab.file_table, QTableWidget):
                    tab.file_table.verticalHeader().setDefaultSectionSize(row_height)
        except Exception as e:
            print(f'[SafeShrink] Settings change error: {e}')

    def apply_language(self, lang):
        """应用语言切换到所有 UI 元素"""
        if lang == 'en-US':
            items = [
                ('📄', 'Slim', 'slim'),
                ('🔒', 'Sanitize', 'sanitize'),
                ('📁', 'Batch', 'batch'),
                ('📋', 'History', 'history'),
                ('⚙️', 'Settings', 'settings'),
            ]
            subtitles = {
                'slim': '📄 Smart compression to reduce file size',
                'sanitize': '🔒 Auto-detect and sanitize sensitive info',
                'batch': '📁 Process multiple files at once',
                'history': '📋 View and manage processing records',
                'settings': '⚙️ Configure preferences',
            }
        else:
            items = self.NAV_ITEMS
            subtitles = {
                'slim': '📄 智能压缩文档，减小文件体积',
                'sanitize': '🔒 自动识别并脱敏敏感信息',
                'batch': '📁 批量处理多个文件',
                'history': '📋 查看和管理处理记录',
                'settings': '⚙️ 配置应用偏好',
            }
        
        # 更新导航栏文字
        for i, (icon, text, key) in enumerate(items):
            list_item = self.nav_list.item(i)
            if list_item:
                list_item.setText(f'  {icon}  {text}')
        
        # 更新当前页面标题
        current = self.nav_list.currentRow()
        if 0 <= current < len(items):
            icon, text, key = items[current]
            self.page_title.setText(text)
            self.page_subtitle.setText(subtitles.get(key, ''))
        
        # 更新各标签页内部 UI
        self._lang = lang
        if hasattr(self.tab_slim, 'update_language'):
            self.tab_slim.update_language(lang)
        if hasattr(self.tab_sanitize, 'update_language'):
            self.tab_sanitize.update_language(lang)
        if hasattr(self.tab_batch, 'update_language'):
            self.tab_batch.update_language(lang)
        if hasattr(self.tab_history, 'update_language'):
            self.tab_history.update_language(lang)
        if hasattr(self.tab_settings, 'update_language'):
            self.tab_settings.update_language(lang)

    def dragEnterEvent(self, event):

        if event.mimeData().hasUrls():

            event.acceptProposedAction()

            self._is_dragging = True

            if self.drag_hint:

                self.drag_hint.resize(300, 60)

                self.drag_hint.move(

                    (self.width() - self.drag_hint.width()) // 2,

                    (self.height() - self.drag_hint.height()) // 2

                )

                self.drag_hint.show()

        else:

            super().dragEnterEvent(event)



    def dragLeaveEvent(self, event):

        if self.drag_hint:

            self.drag_hint.hide()

        self._is_dragging = False

        super().dragLeaveEvent(event)



    def dropEvent(self, event):

        urls = event.mimeData().urls()

        if not urls:

            return



        self.restore_timer.stop()

        self.restore_nav_style()



        paths = [url.toLocalFile() for url in urls]

        files = [p for p in paths if Path(p).is_file()]

        folders = [p for p in paths if Path(p).is_dir()]

        current_index = self.stack.currentIndex()



        if folders:

            if current_index == 2:

                self.tab_batch.set_folder(folders[0])

            else:

                self.nav_list.setCurrentRow(2)

                self.tab_batch.set_folder(folders[0])

        elif files:

            if current_index == 0:

                self.tab_slim.set_file(files[0])

            elif current_index == 1:

                self.tab_sanitize.set_file(files[0])

            elif current_index == 2:

                self.tab_batch.set_folder(str(Path(files[0]).parent))

            else:

                self.nav_list.setCurrentRow(0)

                self.tab_slim.set_file(files[0])



        if self.drag_hint:

            self.drag_hint.hide()

        self._is_dragging = False



    def restore_nav_style(self):

        self.restore_timer.stop()

        self.hovered_nav = -1



    def setup_tray(self):

        try:

            self.tray_icon = QSystemTrayIcon(self)

            self.tray_icon.setToolTip("SafeShrink - 文档工具箱")

            # 优先使用图标文件，否则 fallback

            from PySide6.QtGui import QIcon

            icon = QIcon(str(_get_icon_path()))

            if icon.isNull():

                icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)

            self.tray_icon.setIcon(icon)

            tray_menu = QMenu()

            show_action = QAction("显示主窗口", self)

            show_action.triggered.connect(self.show_from_tray)

            tray_menu.addAction(show_action)

            tray_menu.addSeparator()

            exit_action = QAction("退出", self)

            exit_action.triggered.connect(lambda: sys.exit(0))

            tray_menu.addAction(exit_action)

            self.tray_icon.setContextMenu(tray_menu)

            self.tray_icon.activated.connect(self.on_tray_activated)

            self.tray_icon.show()

        except Exception as e:

            print(f"[SafeShrink] Tray setup error: {e}")

            self.tray_icon = None



    def _get_minimize_to_tray(self):

        import json

        try:

            settings_file = self._get_base_dir() / 'settings.json'

            if settings_file.exists():

                with open(settings_file, 'r', encoding='utf-8') as f:

                    settings = json.load(f)

                return settings.get('minimize_to_tray', False)

        except:

            pass

        return False



    def on_tray_activated(self, reason):

        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:

            self.show_from_tray()



    def show_from_tray(self):

        self.show()

        self.raise_()

        self.activateWindow()



    def _delayed_update_check(self):

        """延迟检查更新，安全的异步检查"""

        try:

            import json

            settings_file = self._get_base_dir() / 'settings.json'

            auto_check = True

            if settings_file.exists():

                with open(settings_file, 'r', encoding='utf-8') as f:

                    settings = json.load(f)

                auto_check = settings.get('auto_check_update', True)



            if not auto_check:

                return



            from update_checker import check_for_updates

            result = check_for_updates()

            if result.get('has_update'):

                msg = f"发现新版本 v{result['latest']}！\n\n"

                msg += f"更新说明：\n{result.get('notes', '暂无')}\n\n"

                msg += "是否前往下载？"

                reply = QMessageBox.question(

                    self, "发现新版本", msg,

                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No

                )

                if reply == QMessageBox.StandardButton.Yes and result.get('url'):

                    import webbrowser

                    webbrowser.open(result['url'])

        except Exception as e:

            print(f"[SafeShrink] Update check error: {e}")



    def closeEvent(self, event):

        # 实时读取设置（确保设置修改后立即生效）

        minimize_to_tray = self._get_minimize_to_tray()

        

        if minimize_to_tray and self.tray_icon and self.tray_icon.isVisible():

            # 勾选最小化到托盘：点×进入托盘

            event.ignore()

            self.hide()

            self.tray_icon.showMessage(

                "SafeShrink",

                "已最小化到托盘，双击图标恢复",

                QSystemTrayIcon.MessageIcon.Information,

                2000

            )

            return

        

        # 未勾选最小化到托盘：弹出确认对话框

        reply = QMessageBox.question(

            self,

            "确认退出",

            "确定要退出 SafeShrink 吗？",

            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,

            QMessageBox.StandardButton.No

        )

        

        if reply == QMessageBox.StandardButton.No:

            event.ignore()

            return

        

        # 确认退出，执行清理

        try:

            self.tab_slim.cleanup()

            self.tab_sanitize.cleanup()

            self.tab_batch.cleanup()

        except Exception as e:

            print(f"[SafeShrink] Cleanup error: {e}")

        

        # 隐藏托盘图标，确保完全退出

        if self.tray_icon:

            self.tray_icon.hide()

        

        event.accept()

        

        # 强制退出应用（因为 setQuitOnLastWindowClosed(False)）

        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()

        if app:

            app.quit()





def _check_single_instance():

    """检查是否已有实例在运行，如果有则提示用户"""

    import ctypes

    from ctypes import wintypes

    

    # 创建互斥锁名称（基于应用名）

    MUTEX_NAME = "Global\\SafeShrink_SingleInstance_Mutex"

    

    # 尝试创建互斥锁

    kernel32 = ctypes.windll.kernel32

    mutex = kernel32.CreateMutexW(None, wintypes.BOOL(False), MUTEX_NAME)

    last_error = kernel32.GetLastError()

    

    if last_error == 183:  # ERROR_ALREADY_EXISTS

        # 已有实例在运行

        kernel32.CloseHandle(mutex)

        return False, None

    

    return True, mutex





def _show_already_running_dialog():

    """显示已有实例运行的提示对话框"""

    from PySide6.QtWidgets import QApplication, QMessageBox

    

    # 创建临时 QApplication 用于显示对话框

    app = QApplication.instance()

    if app is None:

        app = QApplication(sys.argv)

    

    msg_box = QMessageBox()

    msg_box.setWindowTitle("SafeShrink")

    msg_box.setText("SafeShrink 已经在运行")

    msg_box.setInformativeText("检测到已有实例在运行。\n\n是否打开新的窗口？")

    msg_box.setIcon(QMessageBox.Icon.Question)

    

    # 添加按钮

    new_window_btn = msg_box.addButton("打开新窗口", QMessageBox.ButtonRole.AcceptRole)

    bring_to_front_btn = msg_box.addButton("切换到已有窗口", QMessageBox.ButtonRole.DestructiveRole)

    cancel_btn = msg_box.addButton("取消", QMessageBox.ButtonRole.RejectRole)

    

    msg_box.setDefaultButton(bring_to_front_btn)

    msg_box.exec()

    

    if msg_box.clickedButton() == new_window_btn:

        return "new"

    elif msg_box.clickedButton() == bring_to_front_btn:

        return "bring_to_front"

    else:

        return "cancel"





def _bring_existing_window_to_front():

    """将已有窗口带到前台"""

    import ctypes

    from ctypes import wintypes

    

    # 查找 SafeShrink 窗口

    user32 = ctypes.windll.user32

    

    def enum_windows_callback(hwnd, extra):

        if user32.IsWindowVisible(hwnd):

            length = user32.GetWindowTextLengthW(hwnd)

            if length > 0:

                buffer = ctypes.create_unicode_buffer(length + 1)

                user32.GetWindowTextW(hwnd, buffer, length + 1)

                if "SafeShrink" in buffer.value:

                    extra.append(hwnd)

        return True

    

    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    windows = []

    user32.EnumWindows(EnumWindowsProc(enum_windows_callback), ctypes.cast(ctypes.pointer(ctypes.c_int(0)), wintypes.LPARAM))

    

    if windows:

        hwnd = windows[0]

        # 恢复窗口（如果最小化）

        user32.ShowWindow(hwnd, 9)  # SW_RESTORE

        # 带到前台

        user32.SetForegroundWindow(hwnd)

        return True

    return False





if __name__ == '__main__':

    # CLI 模式检测：如果参数含 slim/sanitize/batch/check/json，走 CLI 入口

    _cli_commands = ('slim', 'sanitize', 'batch-slim', 'batch-sanitize')

    _is_cli = any(c in sys.argv for c in _cli_commands) or '--check' in sys.argv or '--json' in sys.argv or '--version' in sys.argv



    if _is_cli:

        # CLI 模式：直接调用 safe_shrink.main()

        sys.exit(safe_shrink_main())

    

    # GUI 模式：检查单实例

    is_first, mutex_handle = _check_single_instance()

    

    if not is_first:

        # 已有实例在运行，显示提示

        try:

            result = _show_already_running_dialog()

            if result == "cancel":

                sys.exit(0)

            elif result == "bring_to_front":

                _bring_existing_window_to_front()

                sys.exit(0)

            # result == "new" 则继续启动新实例

        except Exception as e:

            print(f"[SafeShrink] 单实例检查错误: {e}")

            # 出错时默认退出，避免多开

            sys.exit(1)

    

    # GUI 模式

    try:

        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)

        app.setQuitOnLastWindowClosed(False)  # 托盘模式：关闭窗口不退出程序

        app.setStyle('Fusion')

        font = QFont("Microsoft YaHei", 10)

        if hasattr(font, 'setStyleHint'):

            font.setStyleHint(QFont.StyleHint.SansSerif)

        app.setFont(font)

        window = MainWindow()

        window.show()

        sys.exit(app.exec())

    except Exception as e:

        import traceback

        err = traceback.format_exc()

        print(f"[SafeShrink CRASH]\n{err}", flush=True)

        try:

            from PySide6.QtWidgets import QApplication, QMessageBox

            crash_app = QApplication([])

            QMessageBox.critical(None, "SafeShrink 崩溃", f"错误:\n{e}\n\n详情已输出到控制台")

            crash_app.quit()

        except Exception:

            pass

        input("\n按回车退出...")

