# SafeShrink 密小件 / SafeShrink Document Optimizer

> 一键文档减肥、脱敏、SSD转换，完全离线，保护隐私  
> One-click document slimming, sanitization, and SSD conversion. Fully offline, privacy-first.

**版本：v1.2.1** | [GitHub](https://github.com/JinwaTech/safeshrink) · [下载 EXE](https://github.com/JinwaTech/safeshrink/releases/latest)

---

## ✨ 核心功能 / Core Features

| 功能 / Feature | 说明 / Description | 效果 / Effect |
|------|------|------|
| 🗜️ **文档减肥 / Document Slimming** | 压缩文档体积，去除冗余内容 / Compress document size, remove redundancy | 体积减少 / Size reduced **30%-70%** |
| 🔒 **智能脱敏 / Smart Sanitization** | 自动识别并脱敏敏感信息 / Auto-detect and mask sensitive info | 支持 10+ 种敏感类型 / 10+ sensitive types supported |
| 📝 **SSD 转换 / SSD Conversion** | Office/PDF → .ssd 格式 / Office/PDF → .ssd format | Token 消耗降低 / Token reduced **~70%** |
| 📦 **批量处理 / Batch Processing** | 文件夹一键批量处理 / One-click folder batch processing | 多线程并行，智能跳过 / Multi-threaded, smart skip |
| 🖼️ **OCR 识别 / OCR Recognition** | 扫描件 PDF / 图片自动 OCR / Auto OCR for scanned PDFs/images | 输出可搜索文本 / Searchable text output |

---

## 💰 使用效果 / Usage Results

### 📉 Token 节省对比 / Token Savings

> 基于方案F实测（原文字符×3 vs SSD Markdown token 估算），真实测试数据
> Based on Scheme F actual testing (original chars ×3 vs SSD Markdown token estimate)

| 文档类型 / Document Type | 原始 Token / Original | 转换后 Token / After SSD | 节省 / Saved |
|----------|-----------|-------------|------|
| DOCX → SSD（实测）/ DOCX → SSD (tested) | 5,520 | 1,784 | **67%** |
| 合同.docx (5页) / Contract.docx (5 pages) | ~4,000 | ~1,200 | **~70%** |
| 报告.pptx (20页) / Report.pptx (20 pages) | ~10,000 | ~3,000 | **~70%** |
| 手册.pdf (50页) / Manual.pdf (50 pages) | ~18,000 | ~5,400 | **~70%** |
| 含图片文档 / Image-heavy docs | ~15,000 | ~4,500 | **~70%** |
| 激进压缩 / Aggressive | ~5,520 | ~800 | **~85%** |

**节省原理 / Why so high:**
- Office 文件内部 XML 标签占大量 token（字体、样式、段落属性等），SSD 直接输出 Markdown 结构，XML 开销全部消除 / Office files have heavy XML overhead (fonts, styles, paragraph props); SSD outputs clean Markdown, eliminating all XML bloat
- 隐藏内容（批注、修订、宏）全部清除，不占 token / Hidden content (comments, revisions, macros) removed, zero token cost
- 图片 Base64 可替换为文字描述，大幅降低 token / Images can be replaced with text descriptions, drastically reducing token usage

*按 GPT-4o 价格 ¥0.10/1K tokens 计算 / Calculated at GPT-4o price ¥0.10/1K tokens*

### 📄 转换效果示例 / Conversion Examples

**SSD 转换效果 / SSD Conversion:**
```
📄 合同.docx  →  📄 合同.ssd
- 文字：完整保留 / Text: fully preserved
- 表格：转为 .ssd 表格格式 / Tables: converted to .ssd table format
- 图片：自动 Base64 内嵌（可选压缩）/ Images: auto Base64 embedded (optional compression)
- 格式：去除冗余样式，LLM 更易读 / Formatting: redundant styles removed, LLM-friendly
```

**智能脱敏效果 / Smart Sanitization:**
```
原文 / Original:
联系人：张三，电话：13812345678，报价：500万元
Contact: Zhang San, Phone: 13812345678, Quote: 5 million CNY

脱敏后 / Sanitized:
联系人：张*，电话：138****5678，报价：***
Contact: Z*, Phone: 138****5678, Quote: ***
```

| 类型 / Type | 示例 / Example | 脱敏结果 / Result |
|------|------|----------|
| 手机号 / Phone | `13812345678` | `138****5678` |
| 邮箱 / Email | `test@example.com` | `te***@example.com` |
| 身份证 / ID Card | `110101199001011234` | `110***********1234` |
| 银行卡 / Bank Card | `6222021234567890123` | `622202******0123` |
| IP地址 / IP Address | `192.168.1.1` | `***.***.***.***` |
| 金额 / Amount | `500万元` / `5 million CNY`、`87.81亿元` / `8.78 billion CNY` | `***` |
| 自定义 / Custom | 任意关键词 / Any keyword | 手动配置 / Manual config |

---

## 📖 使用场景 / Use Cases

### 💼 企业合规 / Enterprise Compliance
批量处理合同，脱敏敏感信息后再分享给外部团队
Batch process contracts, sanitize sensitive info before sharing externally

```
📂 /客户资料/
   ├─ 合同A.docx     →  合同A_脱敏.ssd
   ├─ 合同B.pdf      →  合同B_脱敏.ssd
   └─ 报价单.xlsx    →  报价单_脱敏.ssd
```

### 📚 知识库建设 / Knowledge Base
将 Office 文档转为 .ssd 格式，降低 AI 知识库成本
Convert Office docs to .ssd format, reducing AI knowledge base costs

```
📂 /产品文档/
   ├─ 演示文稿.pptx   →  演示文稿.ssd（嵌入图片）
   └─ 技术文档.docx   →  技术文档.ssd（嵌入图片）
```

### 🖼️ 扫描件 OCR / Scanned PDF OCR
对扫描件 PDF 进行 OCR，输出可搜索文本
OCR scanned PDFs, output searchable text

```
📄 扫描合同.pdf  →  📄 扫描合同.ssd（文字可搜索）
```

---

## 🚀 快速开始 / Quick Start

### 方式一：下载 EXE（推荐）/ Option 1: Download EXE (Recommended)

前往 [GitHub Releases](https://github.com/JinwaTech/safeshrink/releases/latest) 下载 `SafeShrink.exe`，双击运行，无需安装。

> ⚠️ **系统要求 / System Requirements**：Windows 8 或更高版本 / Windows 8 or later。不支持 Windows 7（缺少必要的系统 API）。
> ⚠️ **System Requirements**: Windows 8 or later. Windows 7 is not supported (missing required system APIs).

### 方式二：SkillHub 安装 / Option 2: Install via SkillHub

```bash
# 安装 SafeShrink Skill / Install SafeShrink Skill
skillhub install safeshrink
```

### 方式三：源码运行 / Option 3: Run from Source

```bash
# 克隆仓库 / Clone repo
git clone https://github.com/JinwaTech/safeshrink.git
cd safeshrink
# 安装依赖 / Install deps
pip install -r requirements.txt
# 启动 GUI / Launch GUI
python start_gui.py
```

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

## 🛡️ 产品准则 / Product Principles

| 准则 / Principle | 说明 / Description |
|------|------|
| 🔒 **完全离线 / Fully Offline** | 无需联网，数据不出本地 / No internet needed, data stays local |
| 🚫 **零删除 / Zero Deletion** | 保留原文件，输出到新文件夹 / Keep originals, output to new folder |
| 📁 **可回溯 / Traceable** | 处理报告记录所有操作 / Processing report records all operations |
| ⚡ **高效并行 / Efficient Parallel** | 多线程批量处理 / Multi-threaded batch processing |

---

## 📊 性能指标 / Performance Metrics

| 指标 / Metric | 数值 / Value |
|------|------|
| 处理速度 / Processing Speed | ~50 页/秒（文档减肥）/ ~50 pages/sec (slimming) |
| 批量并行 / Batch Parallel | 多线程默认，智能调度 / Multi-threaded by default, smart scheduling |
| 内存占用 / Memory Usage | < 200MB（常规文档）/ < 200MB (typical docs) |
| 支持单文件 / Max Single File | 最大 500MB / Up to 500MB |
| OCR 支持 / OCR Support | 扫描件 PDF + 图片 / Scanned PDFs + images |

---

## 📁 文件说明 / File Index

| 文件 / File | 说明 / Description |
|------|------|
| `README.md` | 用户指南 / User Guide |
| `SKILL.md` | Skill 插件文档 / Skill Plugin Documentation |
| `main_window_v2.py` | 主窗口 UI 源码 / Main Window UI Source |
| `settings_tab.py` | 设置面板源码 / Settings Panel Source |
| `history_manager.py` | 历史记录管理器 / History Manager |
| `history_tab.py` | 历史记录面板 / History Panel |
| `theme_manager.py` | 主题管理器 / Theme Manager |
| `translations.py` | 多语言翻译 / Translations |
| `result_compare_dialog.py` | 结果对比对话框 / Result Compare Dialog |
| `assets/` | 图标与资源文件 / Icons & Resources |
| `requirements.txt` | Python 依赖列表 / Python Dependencies |
| `.gitignore` | Git 忽略规则 / Git Ignore Rules |
| `LICENSES_THIRD_PARTY.txt` | 第三方许可证 / Third-Party Licenses |

---

## 🤝 贡献与支持 / Contributing

- 🐛 [提交 Issue](https://github.com/JinwaTech/safeshrink/issues) / [Submit Issue](https://github.com/JinwaTech/safeshrink/issues)
- 💡 [功能建议](https://github.com/JinwaTech/safeshrink/discussions) / [Feature Request](https://github.com/JinwaTech/safeshrink/discussions)
- ⭐ [Star 支持](https://github.com/JinwaTech/safeshrink) / [Star on GitHub](https://github.com/JinwaTech/safeshrink)

---

## 📄 License / 许可证

**专有软件许可证（Proprietary License）**
**Proprietary License — All Rights Reserved**

© 2026 杭州金蛙信息科技有限公司 版权所有
© 2026 JinwaTech Co., Ltd. All Rights Reserved.

- 本软件为专有软件，受知识产权保护 / Proprietary software, protected by intellectual property rights
- 禁止逆向工程、反编译或修改本软件 / Reverse engineering, decompiling, or modifying prohibited
- 禁止分发、转让或出租本软件 / Distribution, transfer, or rental prohibited
- 详细信息请参阅 LICENSES_THIRD_PARTY.txt / See LICENSES_THIRD_PARTY.txt for details

---

<div align="center">

**SafeShrink 密小件 — 让文档更轻、更安全、更 AI 友好**
**SafeShrink — Lighter Docs, Safer Data, More AI-Friendly**

[GitHub](https://github.com/JinwaTech/safeshrink) · [下载 EXE](https://github.com/JinwaTech/safeshrink/releases/latest) · [问题反馈](https://github.com/JinwaTech/safeshrink/issues)

</div>
