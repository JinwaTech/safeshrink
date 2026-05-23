# SafeShrink 设计文档

> 项目：密小件 · 文档减肥 / 脱敏 / SSD 转换
> 维护者：JinwaTech
> **专有软件许可证（Proprietary License）**
> © 2026 杭州金蛙信息科技有限公司 版权所有
> 
> - 本软件为专有软件，受知识产权保护
> - 禁止逆向工程、反编译或修改本软件
> - 禁止分发、转让或出租本软件
> - 详细信息请参阅 LICENSES_THIRD_PARTY.txt
> - **注意：Skill 包采用 MIT-0 许可证，软件本体为专有软件**

---

## 一、核心定位

对用户：SSD 格式文档（品牌化）
对 AI/LLM：标准 Markdown（保证可解析）

**核心价值**：离线文档处理，保护隐私；压缩体积 + 擦除敏感信息 + 降低 Token 消耗。

---

## 二、技术架构

### 2.1 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.13（venv `.venv313`）|
| GUI 框架 | PySide6（LGPL，可闭源） |
| PDF 处理 | pypdf（BSD）+ pymupdf（OCR 渲染） |
| Word 处理 | python-docx |
| OCR 引擎 | Tesseract v5.4.0（chi_sim+chi_tra+eng） |
| 打包 | PyInstaller 6.20（onedir 模式） |
| 图标 | G-Sketch 单 S 素描风格，cream 背景，圆角透明 |

### 2.2 目录结构

```
SafeShrink/
├── main_window_v2.py      # 主窗口、UI 布局
├── slim_tab.py            # 文档减肥 Tab
├── sanitize_tab.py        # 脱敏 Tab
├── batch_tab.py           # 批量处理 Tab
├── safe_shrink.py         # 核心逻辑（CLI/模块）
├── format_to_ssd.py       # SSD 格式转换实现
├── sanitize_enhanced.py   # 增强脱敏（开发中）
├── main_window_v2.spec    # PyInstaller spec（含 hiddenimports）
├── build_safeshrink.py    # 构建脚本（自动发现 hiddenimports）
├── build.py               # 旧构建脚本（保留）
└── assets/               # 图标等资源
```

### 2.3 三层标记体系

防止文件被重复处理的三重保险：

1. **文件名后缀**：输入文件添加 `_处理结果`、`_脱敏`、`_SSD` 等后缀
2. **隐藏标记文件**：`.safeshrink_processed` / `.safeshrink_skip`
3. **操作类型**：减肥 / 脱敏 / SSD 转换三种模式

---

## 三、核心模块

### 3.1 safe_shrink.py

提供 CLI 和模块双接口。核心函数：

- `slim_docx(input, output, mode)` — .docx 减肥
- `slim_xlsx(input, output)` — .xlsx 减肥
- `slim_pptx(input, output)` — .pptx 减肥
- `slim_pdf(input, output)` — PDF 减肥
- `sanitize_content(text, items)` — 纯文本脱敏
- `estimate_tokens(text_or_bytes, images)` — Token 估算

**Token 估算策略**：
- 文字：文件大小 ÷ 4
- 图片：精确 base64 检测 ÷ 4，兜底 170 token/张

### 3.2 format_to_ssd.py

Office/PDF → SSD（Markdown）格式转换。支持 OCR（Tesseract）预处理。

### 3.3 sanitize_tab.py / batch_tab.py

使用 `DocSanitizer` 类进行脱敏。脱敏类型通过 `options['sanitize_items']` dict 传入，键为中文类型名（手机号、邮箱等），值固定 True（勾选状态）。内部通过 `PATTERNS`（英文 key）匹配，转换通过 `TYPE_MAP`（中文→英文 key）。

**注意**：`DocSanitizer.sanitize()` 期望 `items` 参数为 **list**（如 `['手机号', '邮箱']`），传入 dict 会导致匹配失败。

### 3.4 batch_tab.py 批量处理

- 多线程并行（默认 4 线程）
- 递归扫描子目录
- `skip_names` / `skip_suffixes` 跳过已处理文件
- 对 .md/.txt 文件调用 `_sanitize_text()` 纯文本脱敏
- **输出命名统一**：所有模式后缀 `_减肥`（原 `_处理结果` 已废弃）
- **Office 文件**：标准减肥走原生保留格式（`slim_native_xlsx/pptx`），不走文本提取

### 3.5 单文件 vs 批量处理路径

| 文件类型 | 单文件标准减肥 | 批量标准减肥 |
|---------|--------------|------------|
| docx | `clean_docx_deep()` 临时文件 → 手动保存 | `process_file_gui()` → 原生保留格式 |
| xlsx/pptx | `slim_native_*()` 临时文件 → 手动保存 | `process_file_gui()` → 原生保留格式 |
| pdf | `clean_pdf_metadata()` 临时文件 → 手动保存 | `clean_pdf_metadata()` → 自动输出 |
| txt/md/json/csv/html/xml | `slim_content()` → 手动保存 | `process_file_gui()` → 自动输出 |
| 图片 | `compress_image()` 临时文件 → 手动保存 | 复制原文件（跳过）|

---

## 四、已解决的技术问题

| # | 问题 | 根因 | 解决方案 |
|---|------|------|----------|
| 1 | EXE 闪退 | 回调在属性创建前触发 | 调整初始化顺序 |
| 2 | 最小化退出 | `quitOnLastWindowClosed` 未设 | 添加标志位 |
| 3 | 图标四角深色 | PNG 透明角被 Windows 裁切 | 改用不透明 cream 背景 |
| 4 | 批量处理 KeyError | `items_found: None` 字典访问 | 修复初始化 |
| 5 | 日历弹窗裁切 | `installEventFilter` 未调用 | 添加事件过滤器注册 |
| 6 | 日历导航栏间隙 | 缺统一背景色 | 添加背景色 |
| 7 | 年份选择器按钮 | Qt 内部控件坐标定位失败 | 改用 insertWidget 固定坐标 |
| 8 | 批量脱敏计数 0 | dict/list 类型不匹配 | dict→list 转换 |
| 9 | 脱敏结果未保存 | 写文件用原始 text 而非 sanitized_text | 改用 sanitized_text |
| 10 | 脱敏弹窗显示 0 处 | split("项") 而非 split("处") | 修正解析逻辑 |
| 11 | output 文件夹被跳过 | skip_names 含 'output' | 从 skip_names 移除 |
| 12 | 批量处理完成双弹窗 | QMessageBox 显示期间事件循环继续，递归触发 on_finished 第二次 | 添加 `_batch_compare_shown` 标志拦截重复调用 |
| 13 | 批量处理无法连续执行 | _processing_lock 未在所有退出路径解锁 | 添加 finally 块确保解锁 |
| 14 | 扫描件PDF未开OCR报错 | 纯图片PDF无文本层，SSD转换结果为空 | `format_to_ssd.py` 抛 `NEEDS_OCR` 特殊错误，`slim_tab.py` 捕获后显示友好提示 |
| 15 | 深度清理模式名不一致 | UI显示"保留结构"但代码比较"深度清理" | 统一三处（addItems、tooltip、on_format_changed modes列表） |
| 16 | process_file()静默失败 | Qt事件循环吞掉异常，用户看不到任何提示 | 添加 `try/except` + `QMessageBox.critical()` 全局异常捕获 |
| 17 | NameError: tempfile | `process_text_file()` 调用 `tempfile.mkstemp()` 但未导入 | 顶部添加 `import tempfile` |
| 18 | 单文件状态残留 | `set_file()`/`browse_file()` 未清除 `deep_cleaned_path`/`compressed_path` | 切换文件时 delattr 清除 |
| 19 | PPTX/XLSX 标准压缩报错 | `slim_native_pptx/xlsx()` 返回无 `success` 键，`res.get("success")` 为 None | 返回结构增加 `success: True` |
| 20 | PPTX/XLSX 源目录污染 | 临时文件直接放 `Path(self.current_file).with_suffix(".slim"+ext)` | 改用 `tempfile.gettempdir()` |
| 21 | 批量 SSD 命名泄漏 | `batch_processor.py` 中 `ssd_converted` 变量未初始化，残留上次值 | 在 `action == 'slim'` 前初始化 `ssd_converted = False` |
| 22 | 脱敏计数不准确 | `detect_sensitive()` 与 `DocSanitizer.sanitize()` 匹配策略不对称 | 逐项验证法：每项检查原文本在脱敏后剩余次数 |
| 23 | .docx 批量不处理 | `read_docx()` 调用旧 API `markitdown.convert()`，新版需 `MarkItDown().convert()` | 更新 API + 安装 `markitdown[docx]`（mammoth, cobble）|
| 24 | 批量标准减肥文件无 `_减肥` 后缀 | GBK→UTF-8 编码膨胀导致 `saved_bytes <= 0`，触发删除 `_减肥` 文件并复制原文件（无后缀）；图片走 `compress_image_gui` 绕过后缀逻辑；xlsx/pptx `res.get('result')` 永远为 None（应为 `res.get('success')`） | 文本文件：`compression_rate > 0.5` 改为 `> 0.7` 避免误删括号；图片：输出路径加 `_减肥` 后缀；Office：`res.get('result')` → `res.get('success')`；移除压缩无效时复制原文件逻辑 |
| 25 | 模式切换状态残留 | `on_format_changed()` 只更新 UI 控件，未清除 `deep_cleaned_path`/`compressed_path`，`save_result()` 命中旧路径直接返回 | 在 `on_format_changed()` 末尾增加 `delattr` 清除 `deep_cleaned_path` 和 `compressed_path` |

---

## 五、UI 弹窗规范

所有 QMessageBox 标题/按钮使用中文：
- 标题：`完成`、`错误`、`警告`
- 按钮：Qt 原生按钮文字由系统决定

弹窗消息格式：
- 文档减肥：`{original}KB → {compressed}KB（压缩率 {ratio}%）`
- SSD 转换：`Token: {orig_tok} → {new_tok}，节省 {saved} tokens`
- 脱敏：`已完成脱敏 {count} 处`

---

## 六、版本历史

### v1.2.0（2026-05-23）

**从 v1.1.11 到 v1.2.0 完整变更（commit 071eaef → a74ed64 + 工作区修复）：**

#### 新增功能
- `result_compare_dialog.py`：新增结果对比对话框（文本对比含 Token 估算、图片对比接口）
- `format_to_ssd.py`：新增 xlrd 模块支持 .xls 旧版 Excel 转 SSD（Markdown 表格输出）
- `setup_cython.py`：新增 Cython 编译脚本（编译 safe_shrink.py、batch_processor.py、format_to_ssd.py）

#### 核心修复
- **批量 `_减肥` 后缀缺失**（#24）：GBK→UTF-8 编码膨胀导致 `saved_bytes <= 0` 触发复制原文件无后缀；图片走 `compress_image_gui` 绕过后缀逻辑；xlsx/pptx 返回键判断错误（`result` → `success`）。修复：`compression_rate > 0.7`、图片输出加后缀、Office 返回键修正、移除压缩无效时复制原文件
- **模式切换状态残留**（#25）：`on_format_changed()` 未清除 `deep_cleaned_path`/`compressed_path`，`save_result()` 命中旧路径。修复：模式切换时 `delattr` 清除状态
- **EXE markitdown 打包缺失**：`markitdown → magika → onnxruntime` 依赖链不完整，`MARKITDOWN_AVAILABLE=False`。修复：spec 改为 `collect_all('markitdown')` 收集全部依赖
- **扫描件 PDF 空结果**：markitdown 可用后扫描件返回空字符串而非 None，绕过 `NEEDS_OCR` 检查。修复：`format_to_ssd.py` 增加 PDF 扩展名特殊判断
- **batch_processor.py 错误分类**：except 块未区分错误类型
- **脱敏增强**：价格上下文匹配增至 28 个关键词（价格、报价、投标、成交等）
- **markitdown API 更新**：`markitdown.convert()` → `MarkItDown().convert()`

#### 构建优化
- `build_safeshrink.py`：新增 `verify_build_env()` 和 `save_build_manifest()` 函数
- `main_window_v2.spec`：`collect_submodules` → `collect_all`，覆盖 markitdown/magika/onnxruntime 完整依赖链
- EXE 体积：21.65 MB（onedir 模式，Python 3.13 + PySide6）

#### 其他
- 图片 OCR 输出改为 `.md`（原 `.slim.md`）
- 临时文件统一改用 `tempfile.gettempdir()`
- 清理 Cython 编译产物（11 个 .c 文件）

### v1.1.11（2026-05-23）
- 修复：单文件状态残留 — `set_file()`/`browse_file()` 清除 `deep_cleaned_path`/`compressed_path`
- 修复：PPTX/XLSX 标准压缩 — `slim_native_pptx/xlsx()` 返回 `success: True`，临时文件改 `tempfile.gettempdir()`
- 修复：批量重复文件 — PDF/docx deep clean 输出到临时文件，避免覆盖原文件
- 修复：批量 SSD 命名泄漏 — `ssd_converted = False` 初始化
- 修复：脱敏计数 — 逐项验证法，增强价格上下文匹配（28个关键词）
- 修复：.docx 批量处理 — 更新 markitdown API，添加 mammoth/cobble hiddenimports
- 统一：批量输出命名 `_减肥`（原 `_处理结果` 废弃）
- 构建：EXE 21.65MB，Python 3.13 + PySide6 + Cython .pyd

### v1.1.10（2026-05-22）
- 图标：v13 最终版 — S logo 居中（质心 123,121），圆角半径 42，四角透明化
- 图标：背景扩展至右下边缘，硬编码 RGB(245,240,232) 纯净乳白色
- 图标：7 种嵌入尺寸（16/24/32/48/64/128/256），同步至 19 个位置
- 构建：EXE 18.75 MB，功能验证通过

### v1.1.9（2026-05-21）
- 修复：扫描件PDF未勾选OCR时SSD转换报错 → 改为友好提示"需要开启OCR"
- 修复：`format_to_ssd.py` 抛 `NEEDS_OCR` 特殊错误，`slim_tab.py` 捕获后显示信息框
- 修复：`process_file()` 添加 `try/except` 全局异常捕获，避免Qt静默吞掉错误
- 修复：添加缺失的 `import tempfile`，修复 `NameError`
- 修复：深度清理模式UI名称统一（"保留结构"→"深度清理"）

### v1.1.8（2026-05-12）
- UI修复：单文件/批量 SSD 选项中 "扫描为Markdown" → "扫描为SSD"（slim_tab.py 4处 + batch_tab.py 1处）
- 构建：build.py v2 — `auto-discover_hiddenimports()` 自动扫描本地模块（8个），无需手动维护 hiddenimports 列表
- 构建：main_window_v2.spec 恢复原始状态（移除 `name='SafeShrink'`/`distpath='dist'` 覆盖），由 build.py 处理 EXE 目录重命名
- 构建：build.py `rename_dist()` 兼容两种 PyInstaller 输出模式
- 修复：批量处理双弹窗 — 添加 `_batch_compare_shown` 标志拦截递归调用
- 修复：`_processing_lock` finally 块确保所有退出路径解锁
- 清理：移除所有调试 print 语句和堆栈日志

### v1.1.7（2026-05-10）
- 新增：单文件 PDF OCR — slim_tab.py 增加 `chk_ocr_pdf` 复选框，SSD 模式下显示
- 新增：单文件 PDF OCR 参数传递 — `process_text_file()` → `convert_format_to_ssd()` → `convert_to_ssd_v2()` 完整链路
- 新增：批量 PDF OCR — batch_processor.py / batch_tab.py 支持 `ocr_pdf` 参数
- 新增：`is_scanned_pdf()` 智能检测扫描件 PDF，`ocr_pdf_pages()` 逐页 OCR 渲染
- 修复：单文件模式 PDF OCR 遗漏（批量成功但单文件失败）
- 构建：v1.1.7 EXE 24.08 MB，WinError 32 同步失败需手动复制

### v1.1.6（2026-05-09）
- 修复：尺寸限制区域布局 — 重构输入框布局（移除嵌套），增加 size_group 顶部内边距(12px)，避免标题被上方区域压住
- 修复：quality_layout 和 size_group 之间增加 8px 间距
- 新增：QSpinBox:disabled 样式，确保禁用状态下仍可见
- 修复：_on_resize_toggled 信号连接，启用/禁用尺寸限制时正确控制输入框状态

### v1.1.5（2026-05-09）
- 修复：选"扫描为SSD"后跳回"文件减肥"页面 — `_on_img_format_changed` 中 `format_combo.setCurrentIndex(3)` 触发 `on_format_changed` 信号导致切页
- 修复：彻底移除 `_on_img_format_changed` 中对 `format_combo` 的所有操作，图片模式完全独立于 text 模式
- 新增：build.py 自动同步 EXE 到桌面路径（`sync_to_desktop()`），构建后双保险

### v1.1.4（2026-05-09）
- 新增：图片模式 OCR — Tesseract 集成（lang=chi_sim+eng），用户选择"扫描为SSD"时自动 OCR 图片输出 .ssd
- 新增：slim_tab.py 新增 `process_image_ocr()` 方法，直接调用 `_ocr_image_to_text()`，结果存入 `processed_content`
- 新增：`img_format_combo` 两选项（["图片压缩", "扫描为SSD"]）
- 新增：`_on_img_format_changed()` 回调，index==2 时自动勾选 `img_chk_ocr`
- 修复：`save_result()` OCR 分支：检测 `img_chk_ocr.isChecked()` → 调用 `save_text()` 而非 `save_image()`
- 修复：`_detect_tesseract()` 返回 bool，修复 `tesseract_cmd, version = _detect_tesseract()` 解包报错
- 修复：`format_to_ssd.py` 中 subprocess.run() 添加 startupinfo 隐藏 Tesseract 黑窗口
- 修复：首次拖入图片 stacked_options 未切换到 image_options（debug 构建验证通过）

### v1.1.3（2026-05-08）
- 新增：批量处理 Tab — 多线程并行、图片 OCR 预处理
- 新增：embed_images 默认值改为 False（PPTX 图片 base64 导致 token 爆炸）
- 修复：slider_frame 变量名错误、modes 列表不匹配、4轮迭代完成 v1.1.3
- Tesseract v5.4.0 UB Mannheim 安装验证通过

### v1.1.1（2026-05-05）
- 修复：批量脱敏弹窗解析 "项"→"处"
- 修复：批量 markdown 脱敏 dict→list 类型
- 修复：_sanitize_text 返回值解包修正
- 修复：output 文件夹跳过
- 修复：_SSD 后缀不再被跳过
- 修复：QMessageBox 中文标题

### v1.1.0（2026-04-30）
- 新增：批量处理 Tab
- 新增：SSD 格式转换
- 新增：单文件脱敏（多类型）
- 修复：日历导航栏样式

### v1.0.0（2026-04-16）
- 初始版本：文档减肥核心功能

---

## 七、经验教训

1. **优化后立即 git commit**：避免被后续操作覆盖
2. **eventFilter 必须注册**：定义方法不够，需 `installEventFilter`
3. **Qt 内部控件样式**：app 级 QSS 无法穿透，需实例级 setStyleSheet
4. **PowerShell UTF-8 替换危险**：可能损坏文件编码，禁止用于含中文的 .py 文件
5. **PyInstaller 打包必须用 spec 文件**：直接 `python -m PyInstaller` 会重新生成 spec，丢失 hiddenimports
6. **delete 操作三问原则**：删除前必须确认用途、确认不影响工作、确认不含 .git/