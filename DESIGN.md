# SafeShrink 设计文档

> 项目：密小件 · 文档减肥 / 脱敏 / SSD 转换
> 维护者：JinwaTech
> License: MIT-0

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
| 语言 | Python 3.14+ |
| GUI 框架 | PySide6（LGPL，可闭源） |
| PDF 处理 | pypdf（BSD）+ pymupdf（OCR 渲染） |
| Word 处理 | python-docx |
| OCR 引擎 | Tesseract v5.4.0（chi_sim+chi_tra+eng） |
| 打包 | PyInstaller 6.19（onedir 模式） |
| 图标 | G-Sketch 单 S 素描风格，cream 背景 |

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
├── build.py               # 构建脚本
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
- 修复：选"扫描为Markdown"后跳回"文件减肥"页面 — `_on_img_format_changed` 中 `format_combo.setCurrentIndex(3)` 触发 `on_format_changed` 信号导致切页
- 修复：彻底移除 `_on_img_format_changed` 中对 `format_combo` 的所有操作，图片模式完全独立于 text 模式
- 新增：build.py 自动同步 EXE 到桌面路径（`sync_to_desktop()`），构建后双保险

### v1.1.4（2026-05-09）
- 新增：图片模式 OCR — Tesseract 集成（lang=chi_sim+eng），用户选择"扫描为Markdown"时自动 OCR 图片输出 .md
- 新增：slim_tab.py 新增 `process_image_ocr()` 方法，直接调用 `_ocr_image_to_text()`，结果存入 `processed_content`
- 新增：`img_format_combo` 三选项（["图片压缩", "扫描为Markdown"]，删除了矛盾的"转换为SSD"）
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