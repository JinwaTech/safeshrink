# SafeShrink / SafeShrink Document Optimizer

> **密小件** 帮您让文档变得更轻、更安全、更 AI 友好。
>
> 它一键完成三件事：
> - **压缩** 文档体积，去除冗余 — **减小 30%-85%**
> - **脱敏** 敏感信息（手机号、证件号、银行卡、金额）— 分享前保护隐私
> - **转换** 为 .ssd 格式 — **AI Token 减少约 70%**
>
> 所有处理 **完全离线** — 数据不会离开您的电脑。无需安装，下载 EXE 双击即用。
>
> ---
>
> **SafeShrink** helps you make documents **lighter, safer, and more AI-friendly**.
>
> It does three things in one click:
> - **Compress** document size, removing redundancy — **30%-85% smaller**
> - **Sanitize** sensitive info (phone numbers, IDs, bank cards, amounts) — privacy protected before sharing
> - **Convert** to .ssd format — **~70% fewer AI tokens**
>
> All processing is **fully offline** — your data never leaves your computer. No installation needed, just download the EXE and double-click.

---


**版本：v1.2.1 / Version: v1.2.1** *(2026-05-24)*

| 功能 / Feature | 说明 / Description | 效果 / Effect |
|------|------|------|
| 🗜️ **文档减肥 / Document Slimming** | 压缩文档体积，去除冗余内容，保留结构 / Compress document size, remove redundancy, preserve structure | Token 节省 / Token Saved **40%-85%** |
| 🔒 **智能脱敏 / Smart Sanitization** | 自动识别并脱敏手机号、身份证、银行卡、金额等 / Auto-detect and mask phone numbers, IDs, bank cards, amounts, etc. | 支持 10+ 种敏感类型 / 10+ sensitive types supported |
| 📝 **SSD 转换 / SSD Conversion** | DOCX/PPTX/XLSX/PDF → .ssd，图片自动 Base64 内嵌 / DOCX/PPTX/XLSX/PDF → .ssd with embedded images | Token 节省 / Token Saved **~70%** |
| 📦 **批量处理 / Batch Processing** | 支持文件夹一键批量处理，智能跳过已处理文件 / Folder batch processing with smart skip | 多线程并行 / Multi-threaded parallel |
| 🖼️ **OCR 识别 / OCR Recognition** | 扫描件 PDF / 图片自动 OCR，输出可搜索文本 / Auto OCR for scanned PDFs/images | 输出可搜索文本 / Searchable text output |

---

## 更新日志 / Changelog

### v1.2.1（2026-05-24）

- **源码保护 / Source Code Protection**: 11 个核心模块编译为 Cython .pyd（safe_shrink、batch_processor、slim_tab 等） / 11 core modules compiled to Cython .pyd
- **源码保护 / Source Code Protection**: GitHub 历史版本（v1.0.0~v1.2.0）已删除，仅保留 v1.2.1 Release / GitHub history versions (v1.0.0~v1.2.0) removed, only v1.2.1 Release retained
- **修复 / Fix**: 单文档脱敏 `[Errno 22] Invalid argument` — `load_file_content()` 未设置 `self._current_file_path` / Single-document sanitization error — `load_file_content()` not setting `self._current_file_path`
- **修复 / Fix**: Cython 循环依赖 — `safe_shrink.py` 自引用导入导致编译失败 / Cython circular import — `safe_shrink.py` self-referencing import causing build failure
- **新增 / New**: CLI 命令体系（slim/batch-slim/convert/compress-image/batch-convert/batch-compress-image）/ CLI command system
- **新增 / New**: `result_compare_dialog.py` 结果对比对话框（文本 Token 对比 + 图片对比）/ Result comparison dialog (text token + image comparison)
- **构建 / Build**: EXE 20.67MB，Python 3.13 + PySide6 + Cython .pyd

### v1.2.0（2026-05-23）

- **修复 / Fix**: 批量减肥 `_减肥` 后缀缺失 — `batch_tab.py` 统一命名逻辑，`saved_bytes <= 0` 增加 `and not is_direct` 条件 / Batch slimming `_减肥` suffix missing
- **修复 / Fix**: PPTX/XLSX 标准压缩报错 — `safe_shrink_gui.py` 检查 `res.get('success')` 而非 `res.get('result')` / PPTX/XLSX standard compression error
- **修复 / Fix**: 模式切换状态残留 — `on_format_changed()` 末尾清除 `deep_cleaned_path` / `compressed_path` / Mode switch state leakage
- **修复 / Fix**: SSD 命名泄漏 — `batch_processor.py` 独立处理命名，不污染批量 Tab / SSD naming leakage
- **修复 / Fix**: sanitize 逐项目验证 — `safe_shrink_gui.py` 确保每项脱敏结果独立确认 / Sanitize item-by-item verification
- **修复 / Fix**: markitdown EXE 打包 — `main_window_v2.spec` 使用 `collect_all('markitdown')` / markitdown EXE packaging
- **构建 / Build**: 清理 Cython `.c` 文件（batch_processor.c 等 5 个）/ Clean Cython `.c` files
- **文档 / Docs**: DESIGN.md 更新至 v1.2.0

### v1.1.8（2026-05-12）

- **修复 / Fix**: 批量处理双弹窗 — 添加 `_batch_compare_shown` 标志拦截递归调用 / Batch processing double popup
- **修复 / Fix**: `_processing_lock` finally 块确保所有退出路径解锁 / `_processing_lock` finally block
- **修复 / Fix**: 批量处理卡死 — 移除 `setDaemon` + 新增 `terminate_worker` + closeEvent 任务检测 / Batch processing freeze
- **修复 / Fix**: 进程残留 — 托盘退出调用 cleanup + build 强制终止残留进程 / Process residue
- **UI 修复 / UI Fix**: 单文件/批量 SSD 选项中 "扫描为Markdown" → "扫描为SSD"（5处）/ "Scan to Markdown" → "Scan to SSD"
- **构建 / Build**: build.py v2 — `auto-discover hiddenimports()` 自动扫描本地模块（8个），无需手动维护 / build.py v2
- **构建 / Build**: spec 文件恢复原始状态，由 build.py 处理 EXE 目录重命名 / spec file restored

### v1.1.7（2026-05-10）

- **新增 / New**: 单文件 PDF OCR — `chk_ocr_pdf` 复选框，SSD 模式下显示 / Single-file PDF OCR
- **新增 / New**: 批量 PDF OCR — `batch_processor.py` / `batch_tab.py` 支持 `ocr_pdf` 参数 / Batch PDF OCR
- **新增 / New**: `is_scanned_pdf()` 智能检测扫描件，`ocr_pdf_pages()` 逐页 OCR 渲染 / Scanned PDF detection

### v1.1.6（2026-05-09）

- **修复 / Fix**: 尺寸限制区域布局 — 重构输入框布局，增加间距，避免被上方区域压住 / Size limit area layout
- **新增 / New**: QSpinBox:disabled 样式，确保禁用状态下仍可见 / QSpinBox:disabled style

### v1.1.5（2026-05-09）

- **修复 / Fix**: 选"扫描为SSD"后跳回"文件减肥"页面 — 彻底移除 `_on_img_format_changed` 中对 `format_combo` 的操作 / Jump back to slimming page after selecting SSD
- **新增 / New**: build.py 自动同步 EXE 到桌面 / build.py auto-sync EXE to desktop

### v1.1.4（2026-05-09）

- **新增 / New**: 图片模式 OCR — Tesseract v5.4.0 集成（chi_sim+eng），用户选择"扫描为SSD"时自动 OCR / Image mode OCR with Tesseract v5.4.0
- **新增 / New**: `img_format_combo` 两选项（"图片压缩" / "扫描为SSD"）/ Two image format options
- **修复 / Fix**: `subprocess.run()` 添加 startupinfo 隐藏 Tesseract 黑窗口 / Hide Tesseract console window

### v1.1.3（2026-05-08）

- **新增 / New**: 批量处理 Tab — 多线程并行、图片 OCR 预处理 / Batch processing Tab
- **修复 / Fix**: SSD 转换默认 `embed_images=False`，避免 PPTX 多图文件 token 暴涨 / SSD default `embed_images=False`
- **修复 / Fix**: slider_frame 变量名错误、modes 列表不匹配 / Variable name errors

---

## ⚠️ 重要提示 / Important Notices

### 前置依赖 / Prerequisites

> 运行 SafeShrink 前，请确保已安装 **Visual C++ Redistributable**。如果启动时提示"找不到 VCRUNTIME140_1.dll"或"MSVCP140.dll 丢失"，请下载并安装：
>
> - 🔗 [VC++ Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)
> - 🔗 [VC++ Redistributable (x86)](https://aka.ms/vs/17/release/vc_redist.x86.exe)
>
> ⚠️ **重要 / Important：** SafeShrink 的 `_internal` 文件夹已包含所有第三方依赖，但仍需要您电脑安装 VC++ 运行时。这是因为 DLL 文件本身依赖微软的系统库，这部分无法打包进 EXE。
>
> ---
>
> Before running SafeShrink, please ensure **Visual C++ Redistributable** is installed. If you see an error like "VCRUNTIME140_1.dll not found" or "MSVCP140.dll missing", please download and install:
>
> - 🔗 [VC++ Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)
> - 🔗 [VC++ Redistributable (x86)](https://aka.ms/vs/17/release/vc_redist.x86.exe)
>
> ⚠️ **Important:** SafeShrink's `_internal` folder contains all third-party dependencies, but your system still needs the VC++ runtime. DLL files depend on Microsoft's system libraries, which cannot be packaged into the EXE.

### 杀毒软件提示 / Antivirus Notice

> ⚠️ **如果 SafeShrink 被杀毒软件拦截，这是误报。**
>
> SafeShrink 是**纯本地**的文件预处理工具，**不联网、不连接任何服务端、不上传任何数据**，不存在数据泄露风险。它**不会修改系统文件、不会安装驱动、不会驻留后台**，不会对电脑造成任何损害。
>
> 被拦截的原因是：SafeShrink 使用 PyInstaller 打包成独立 EXE，这类"单文件可执行程序"在杀毒软件中属于低信誉类别，容易被误判。
>
> **⚠️ 特别提醒 / Special Notice：** 杀毒软件可能会逐个扫描 `_internal` 文件夹中的数百个 DLL 文件，**隔离其中任何一个关键 DLL 都会导致 EXE 启动失败或功能异常**。
>
> **解决方法 / Solution：** 将 SafeShrink 整个文件夹（包括 `_internal`）加入杀毒软件白名单/排除项。如有疑虑，可用 [VirusTotal](https://www.virustotal.com) 上传检测验证。
>
> ---
>
> ⚠️ **If SafeShrink is blocked by your antivirus, it is a false positive.**
>
> SafeShrink is a **fully offline** file preprocessing tool — **no internet, no server connection, no data upload**. Zero risk of data leakage. It **does not modify system files, install drivers, or run in the background**.
>
> **Special Notice:** Antivirus software may scan hundreds of DLL files in the `_internal` folder one by one. **Isolating any critical DLL will cause the EXE to fail to start or malfunction.**
>
> **Solution:** Add the entire SafeShrink folder (including `_internal`) to your antivirus whitelist/exclusions. For verification, upload to [VirusTotal](https://www.virustotal.com).

### 常见问题 / FAQ

| 问题 / Problem | 原因 / Cause | 解决方法 / Solution |
|------|------|------|
| **双击 EXE 没反应 / EXE does nothing** | 杀毒软件静默隔离了 `_internal` 中的某个 DLL / Antivirus silently isolated a DLL in `_internal` | 检查杀毒软件隔离区，恢复所有 SafeShrink 相关文件，并将整个文件夹加入白名单 / Check quarantine, restore all SafeShrink files, add folder to whitelist |
| **提示"找不到 xxx.dll" / "xxx.dll not found"** | VC++ 运行时未安装 / VC++ runtime not installed | 安装 [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) / Install VC++ Redistributable |
| **提示"api-ms-win-core-*.dll 丢失" / "api-ms-win-core-*.dll missing"** | Windows 版本过低 / Windows version too old | SafeShrink 需要 Windows 8 或更高版本 / Requires Windows 8 or later |
| **"转换结果为空" / "Conversion result is empty"** | `_internal` 中的某个依赖 DLL 被杀毒软件隔离 / A dependency DLL in `_internal` was isolated | 检查杀毒软件隔离区，恢复文件并加入白名单 / Check quarantine, restore files and add to whitelist |
| **批量处理中途崩溃 / Batch processing crashes** | 杀毒软件在处理过程中隔离了关键 DLL / Antivirus isolated a critical DLL during processing | 将 SafeShrink 文件夹加入白名单后重试 / Add folder to whitelist and retry |

---

## 📋 支持格式 / Supported Formats

| 类型 / Type | 格式 / Formats | 减肥 / Slim | 脱敏 / Sanitize | SSD |
|------|------|:----:|:----:|:--------:|
| **Office** | .docx, .xlsx, .pptx | ✅ | ✅ | ✅ |
| **PDF** | .pdf | ✅ | ✅ | ✅ |
| **网页 / Web** | .html, .htm | ✅ | ✅ | ✅ |
| **文本 / Text** | .txt, .ssd, .json, .csv | ✅ | ✅ | — |
| **图片 / Image** | .jpg, .png, .gif, .webp | ✅ | — | — |
| **代码 / Code** | .js, .py, .ts, .css, .sql | ✅ | ✅ | ✅ |

---

## 🔐 脱敏范围 / Sanitization Scope

| 类型 / Type | 示例 / Example |
|------|------|
| 手机号 / Phone | `13812345678` → `138****5678` |
| 邮箱 / Email | `test@example.com` → `te***@example.com` |
| 身份证 / ID Card | `110101199001011234` → `110***********1234` |
| 银行卡 / Bank Card | `6222021234567890123` → `622202******0123` |
| IP地址 / IP Address | `192.168.1.1` → `***.***.***.***` |
| 金额 / Amount | `500万元`、`87.81亿元`、`350,000` → `***` |
| 自定义 / Custom | 自定义敏感词手动添加 / Custom keywords manually added |

---

## 📖 使用场景 / Use Cases

### 场景一：企业合规 / Scenario 1: Enterprise Compliance

批量处理合同文件夹，脱敏敏感信息后再分享  
Batch process contract folder, sanitize sensitive info before sharing

```
📂 /客户资料 / /customer-data/
   ├─ 合同A.docx     →  合同A_脱敏.ssd
   ├─ 合同B.pdf      →  合同B_脱敏.ssd
   └─ 报价单.xlsx     →  报价单_脱敏.ssd
```

### 场景二：知识管理 / Scenario 2: Knowledge Management

将 Word/PPT 转为 SSD 格式，图片自动 Base64 内嵌，单文件即可分享  
Convert Word/PPT to SSD format with embedded images for single-file sharing

```
📂 /产品文档 / /product-docs/
   ├─ 演示文稿.pptx   →  演示文稿.ssd（含嵌入图片）
   └─ 技术文档.docx   →  技术文档.ssd（含嵌入图片）
```

### 场景三：扫描件 OCR / Scenario 3: Scanned Document OCR

对扫描件 PDF 进行 OCR，输出可搜索的文本  
OCR scanned PDFs to searchable text

```
📄 扫描合同.pdf  →  📄 扫描合同.ssd（文字可搜索）
```

---

## 🛡️ 软件准则 / Software Principles

| 准则 / Principle | 说明 / Description |
|------|------|
| 🔒 **隐私优先 / Privacy First** | 完全离线处理，数据不外传 / Fully offline, data never leaves local |
| 🚫 **零删除 / Zero Deletion** | 只压缩/脱敏，不删除原始内容 / Only compress/sanitize, never delete original content |
| 📁 **可回溯 / Traceable** | 保留原文件，输出到 output 文件夹 / Keep originals, output to output folder |
| ⚡ **批量高效 / Batch Efficient** | 支持文件夹批量处理，智能跳过已处理文件 / Folder batch processing with smart skip |

---

## 🚀 快速开始 / Quick Start

### 下载 EXE（推荐）/ Download EXE (Recommended)

```bash
# 下载 SafeShrink.exe，双击运行
# Download SafeShrink.exe, double-click to run
https://github.com/JinwaTech/safeshrink/releases
```

### 源码运行 / Run from Source

```bash
# 克隆仓库 / Clone repo
git clone https://github.com/JinwaTech/safeshrink.git
cd safeshrink

# 安装依赖 / Install dependencies
pip install -r requirements.txt

# 启动 / Launch
python main_window_v2.py
```

### SkillHub 安装 / Install via SkillHub

```bash
skillhub install safeshrink
```

---

## 📁 项目结构 / Project Structure

```
SafeShrink/
├── main_window_v2.py      # 主窗口、UI 布局 / Main window, UI layout
├── slim_tab.py            # 文档减肥 Tab（支持图片 OCR）/ Document slimming Tab
├── sanitize_tab.py        # 脱敏 Tab / Sanitization Tab
├── batch_tab.py           # 批量处理 Tab（多线程并行）/ Batch processing Tab
├── safe_shrink.py         # 核心逻辑（CLI/模块）/ Core logic (CLI/module)
├── safe_shrink_gui.py     # GUI 辅助逻辑 / GUI helper logic
├── format_to_ssd.py       # SSD 格式转换实现（含 OCR 预处理）/ SSD conversion (with OCR)
├── batch_processor.py     # 批量处理引擎 / Batch processing engine
├── settings_tab.py        # 设置 Tab / Settings Tab
├── theme_manager.py       # 主题管理 / Theme management
├── history_manager.py     # 历史记录管理 / History management
├── file_status.py         # 处理状态检测 / File status detection
├── _ooxml_to_ssd.py       # Office 降级后备方案 / Office fallback
├── main_window_v2.spec    # PyInstaller spec
├── build.py               # 构建脚本（auto-discover hiddenimports）/ Build script
└── requirements.txt       # Python 依赖 / Python dependencies
```

---

## 🛠️ 技术栈 / Tech Stack

| 技术 / Technology | 用途 / Purpose |
|------|------|
| Python 3.14 + PySide6（LGPL）| GUI 界面 / GUI |
| pypdf / pdfplumber / PyMuPDF | PDF 处理 / PDF processing |
| python-docx / openpyxl / python-pptx | Office 处理 / Office processing |
| pdfminer.six | PDF 文本提取 / PDF text extraction |
| Pillow | 图片处理 / Image processing |
| Tesseract v5.4.0（chi_sim+chi_tra+eng）| OCR 引擎 / OCR engine |
| 正则表达式 / Regex | 敏感信息识别 / Sensitive info detection |

---

## 🤝 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！  
Welcome to submit Issues and Pull Requests!

---

## 📄 License

**专有软件许可证（Proprietary License）**

© 2026 杭州金蛙信息科技有限公司 版权所有  
© 2026 Hangzhou Jinwa Technology Co., Ltd. All Rights Reserved

- 本软件为专有软件，受知识产权保护  
  This software is proprietary, protected by intellectual property rights
- 禁止逆向工程、反编译或修改本软件  
  Reverse engineering, decompilation, or modification is prohibited
- 禁止分发、转让或出租本软件  
  Distribution, transfer, or rental is prohibited
- 详细信息请参阅 LICENSES_THIRD_PARTY.txt  
  See LICENSES_THIRD_PARTY.txt for details

---

## 🔗 相关链接 / Related Links

- [GitHub 仓库 / GitHub Repo](https://github.com/JinwaTech/safeshrink)
- [SkillHub](https://skillhub.com/skills/safeshrink)
- [问题反馈 / Issue Feedback](https://github.com/JinwaTech/safeshrink/issues)

---

<div align="center">

**如果对你有帮助，欢迎 ⭐ Star 支持！ / If this helps you, please ⭐ Star to support!**

</div>
